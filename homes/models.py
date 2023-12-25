from typing import TYPE_CHECKING
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from plotly import express as px
from shortuuid.django_fields import ShortUUIDField

from core.constants import WEEKLY_ACTIVITY_RANGES

if TYPE_CHECKING:
    from residents.models import Resident


class Home(models.Model):
    name = models.CharField(max_length=25)
    # add a foreign key relationship to HomeGroup
    home_group = models.ForeignKey(
        to="homes.HomeGroup",
        on_delete=models.PROTECT,
        related_name="homes",
        null=True,
        blank=True,
    )

    url_uuid = ShortUUIDField(
        _("UUID used in URLs"),
        editable=False,  # type: ignore
    )

    class Meta:
        db_table = "home"
        verbose_name = _("home")
        verbose_name_plural = _("homes")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("home-detail-view", kwargs={"url_uuid": self.url_uuid})

    @property
    def resident_counts_by_activity_level(self) -> dict[str, int]:
        from metrics.models import (
            ResidentActivity,
        )  # Assuming ResidentActivity is in metrics.models

        # Define date range
        today = timezone.now()
        a_week_ago = today - timedelta(days=7)

        # Query ResidentActivity and annotate each resident with their activity count
        annotated_residents = (
            ResidentActivity.objects.filter(
                home=self,
                activity_date__gte=a_week_ago,
            )
            .values("resident_id")
            .annotate(activity_count=Count("id"))
        )

        # Initialize counts
        activity_counts = {
            "total_count": annotated_residents.count(),
            "inactive_count": 0,
            "low_active_count": 0,
            "good_active_count": 0,
            "high_active_count": 0,
        }

        # Categorize each resident into an activity level
        for resident in annotated_residents:
            activity_count = resident["activity_count"]
            if activity_count in WEEKLY_ACTIVITY_RANGES["inactive"]["range"]:
                activity_counts["inactive_count"] += 1
            elif activity_count in WEEKLY_ACTIVITY_RANGES["low"]["range"]:
                activity_counts["low_active_count"] += 1
            elif activity_count in WEEKLY_ACTIVITY_RANGES["good"]["range"]:
                activity_counts["good_active_count"] += 1
            elif activity_count in WEEKLY_ACTIVITY_RANGES["high"]["range"]:
                activity_counts["high_active_count"] += 1
        if activity_counts["total_count"] != 0:
            activity_counts["inactive_percent"] = (
                activity_counts["inactive_count"] / activity_counts["total_count"]
            ) * 100
            activity_counts["low_active_percent"] = (
                activity_counts["low_active_count"] / activity_counts["total_count"]
            ) * 100
            activity_counts["good_active_percent"] = (
                activity_counts["good_active_count"] / activity_counts["total_count"]
            ) * 100
            activity_counts["high_active_percent"] = (
                activity_counts["high_active_count"] / activity_counts["total_count"]
            ) * 100
        else:
            activity_counts["inactive_percent"] = 0
            activity_counts["low_active_percent"] = 0
            activity_counts["good_active_percent"] = 0
            activity_counts["high_active_percent"] = 0

        return activity_counts

    @property
    def resident_counts_by_activity_level_chart_data(self):
        activity_level_counts = self.resident_counts_by_activity_level

        chart_data = [
            {
                "home_name": self.name,
                "activity_level_label": str(
                    WEEKLY_ACTIVITY_RANGES["inactive"]["label"],
                ),
                "value": activity_level_counts["inactive_percent"],
            },
            {
                "home_name": self.name,
                "activity_level_label": str(WEEKLY_ACTIVITY_RANGES["low"]["label"]),
                "value": activity_level_counts["low_active_percent"],
            },
            {
                "home_name": self.name,
                "activity_level_label": str(WEEKLY_ACTIVITY_RANGES["good"]["label"]),
                "value": activity_level_counts["good_active_percent"],
            },
            {
                "home_name": self.name,
                "activity_level_label": str(WEEKLY_ACTIVITY_RANGES["high"]["label"]),
                "value": activity_level_counts["high_active_percent"],
            },
        ]

        return chart_data

    @property
    def resident_percents_by_activity_level_chart(self):
        chart_data = self.resident_counts_by_activity_level_chart_data

        fig = px.bar(
            chart_data,
            x="value",
            y="home_name",
            color="activity_level_label",
            orientation="h",
            labels={
                "value": str(_("Percent of Residents")),
                "home_name": "Home",
                "activity_level_label": "Activity Level",
            },
            # dark theme
            template="plotly_dark",
            # bar height smaller
            barmode="group",
            # height=50,
            # show values on bars
            text="value",
        )

        fig.update_layout(
            autosize=False,
            legend=dict(
                orientation="h",
                # yanchor="top",
                # xanchor="left",
                title=None,
                # remove legend background
                bgcolor="rgba(0,0,0,0)",
            ),
            # hide legend
            # showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            # remove empty space along top of chart
            height=70,
            yaxis=dict(
                showticklabels=False,
            ),
            xaxis=dict(
                showticklabels=False,
                showgrid=False,
                title=None,
            ),
            yaxis_title=None,
        )

        return fig.to_html(
            include_plotlyjs=True,
            full_html=False,
            config={"displayModeBar": False},
        )

    @property
    def current_residents(self) -> models.QuerySet["Resident"]:
        """Returns a QuerySet of all current residents for this home."""
        # avoid circular import
        from residents.models import Resident

        return Resident.objects.filter(
            residency__home=self,
            residency__move_out__isnull=True,
        ).order_by("first_name")


class HomeGroup(models.Model):
    name = models.CharField(max_length=25)

    url_uuid = ShortUUIDField(
        _("UUID used in URLs"),
        editable=False,  # type: ignore
    )

    class Meta:
        db_table = "home_group"
        verbose_name = _("home group")
        verbose_name_plural = _("home groups")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("home-group-detail-view", kwargs={"url_uuid": self.url_uuid})
