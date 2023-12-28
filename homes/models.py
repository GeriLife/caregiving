import datetime
from typing import TYPE_CHECKING
from django.db.models import Count, Q, QuerySet
from django.utils import timezone
from datetime import date, timedelta
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import pandas as pd
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
    def current_residents(self) -> models.QuerySet["Resident"]:
        """Returns a QuerySet of all current residents for this home."""
        # avoid circular import
        from residents.models import Resident

        return Resident.objects.filter(
            residency__home=self,
            residency__move_out__isnull=True,
        ).order_by("first_name")

    @property
    def current_residents_with_recent_activity_metadata(self):
        from metrics.models import ResidentActivity

        current_residents = self.current_residents.all()

        # Generate date range for the last 7 days
        today = date.today()
        days_ago = 7
        date_range = [today - timedelta(days=x) for x in range(days_ago)]

        # Create all combinations of residents and dates
        resident_date_combinations = [
            {
                "resident_id": resident.id,
                "resident_full_name": resident.full_name,
                "activity_date": activity_date,
            }
            for resident in current_residents
            for activity_date in date_range
        ]

        # Convert to DataFrame for easier processing
        df_combinations = pd.DataFrame(resident_date_combinations)

        # Get ResidentActivity data
        activities = (
            ResidentActivity.objects.filter(
                resident__in=current_residents,
                activity_date__gte=date_range[-1],
            )
            .values(
                "resident_id",
                "activity_date",
            )
            .annotate(activity_count=Count("id"))
        )

        df_activities = pd.DataFrame(list(activities))

        # Merge and annotate
        # Left join the combinations with activities
        result = pd.merge(
            df_combinations,
            df_activities,
            how="left",
            on=["resident_id", "activity_date"],
        )

        # Fill NaN in activity_count with 0 and add had_activity column
        # result["activity_count"] = result["activity_count"].fillna(0)
        result["had_activity"] = result["activity_count"] > 0

        # Pivot the DataFrame
        pivot_had_activity = result.pivot_table(
            index=["resident_id", "resident_full_name"],
            columns="activity_date",
            values="had_activity",
            fill_value=False,  # Fill missing values with False
        )

        # Calculate total activity count for each resident
        total_activity_count = (
            result.groupby(
                [
                    "resident_id",
                    "resident_full_name",
                ],
            )["activity_count"]
            .sum()
            .reset_index()
        )
        total_activity_count.rename(
            columns={"activity_count": "total_activity_count"},
            inplace=True,
        )

        # Merge the had_activity pivot with the total activity count
        pivot_result = pd.merge(
            pivot_had_activity.reset_index(),
            total_activity_count,
            on=["resident_id", "resident_full_name"],
            how="left",
        )

        # Sort the final DataFrame by resident_full_name
        pivot_result = pivot_result.sort_values(by="resident_full_name")

        # Convert the DataFrame to a more structured format
        residents_data = []
        for index, row in pivot_result.iterrows():
            resident_data = {
                "resident": current_residents.get(id=row["resident_id"]),
                "total_activity_count": row["total_activity_count"],
                "recent_activity_days": [
                    {"date": date, "was_active": row[date]}
                    for date in pivot_result.columns
                    if isinstance(date, datetime.date)
                ],
            }

            # count the total days where is_active is true
            resident_data["total_active_days"] = sum(
                [
                    1
                    for day in resident_data["recent_activity_days"]
                    if day["was_active"]
                ],
            )

            residents_data.append(resident_data)

        # add the start_date and end_date to the structured data along with residents data
        structured_data = {
            "start_date": date_range[-1],
            "end_date": date_range[0],
            "residents": residents_data,
        }

        return structured_data

    @property
    def residents_with_recent_activity_counts(self) -> QuerySet["Resident"]:
        """Returns a QuerySet of all current residents for this home, annotated
        with a count of recent activities."""
        # Define date range
        today = timezone.now()
        a_week_ago = today - timedelta(days=7)

        # Get current residents
        current_residents = self.current_residents

        # Annotate each resident with a count of recent activities
        residents_with_activities = current_residents.annotate(
            recent_activity_count=Count(
                "resident_activities",
                filter=Q(
                    resident_activities__activity_date__gte=a_week_ago,
                    resident_activities__activity_date__lte=today,
                ),
            ),
        )

        return residents_with_activities

    @property
    def resident_counts_by_activity_level(self) -> dict[str, int]:
        """Returns a dictionary of counts of residents by activity level."""

        annotated_residents = self.residents_with_recent_activity_counts

        # Initialize counts
        activity_counts = {
            "total_count": annotated_residents.count(),
            "inactive_count": 0,
            "low_active_count": 0,
            "good_active_count": 0,
            "high_active_count": 0,
        }

        # Categorize each resident into an activity level
        # and increment the appropriate count
        for resident in annotated_residents:
            activity_count = resident.recent_activity_count

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
    def resident_counts_by_activity_level_chart_data(self) -> list[dict]:
        """Returns a list of dictionaries of counts of residents by activity
        level."""

        activity_level_counts = self.resident_counts_by_activity_level

        if not self.resident_counts_by_activity_level["total_count"]:
            return []

        chart_data = [
            {
                "activity_level_label": str(
                    WEEKLY_ACTIVITY_RANGES["inactive"]["label"],
                ),
                "activity_level_class": WEEKLY_ACTIVITY_RANGES["inactive"][
                    "color_class"
                ],
                "value": activity_level_counts["inactive_percent"],
            },
            {
                "activity_level_label": str(WEEKLY_ACTIVITY_RANGES["low"]["label"]),
                "activity_level_class": WEEKLY_ACTIVITY_RANGES["low"]["color_class"],
                "value": activity_level_counts["low_active_percent"],
            },
            {
                "activity_level_label": str(WEEKLY_ACTIVITY_RANGES["good"]["label"]),
                "activity_level_class": WEEKLY_ACTIVITY_RANGES["good"]["color_class"],
                "value": activity_level_counts["good_active_percent"],
            },
            {
                "activity_level_label": str(WEEKLY_ACTIVITY_RANGES["high"]["label"]),
                "activity_level_class": WEEKLY_ACTIVITY_RANGES["high"]["color_class"],
                "value": activity_level_counts["high_active_percent"],
            },
        ]

        return chart_data


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
