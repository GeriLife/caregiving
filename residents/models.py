from typing import TYPE_CHECKING
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from shortuuid.django_fields import ShortUUIDField
from core.constants import WEEKLY_ACTIVITY_RANGES
from homes.models import Home

if TYPE_CHECKING:
    from metrics.models import ResidentActivity


class Resident(models.Model):
    first_name = models.CharField(max_length=255)
    last_initial = models.CharField(max_length=1)
    on_hiatus = models.BooleanField(default=False)

    url_uuid = ShortUUIDField(
        _("UUID used in URLs"),
        editable=False,  # type: ignore
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_initial}"

    class Meta:
        db_table = "resident"
        verbose_name = _("resident")
        verbose_name_plural = _("residents")

    def __str__(self) -> str:
        return self.full_name

    def get_absolute_url(self):
        return reverse("resident-detail-view", kwargs={"url_uuid": self.url_uuid})

    def get_recent_activities(self) -> models.QuerySet["ResidentActivity"]:
        """Return a queryset of the resident's activities in the past seven
        days."""
        one_week_ago = timezone.now() - timezone.timedelta(days=7)
        return self.resident_activities.filter(activity_date__gte=one_week_ago)

    def get_recent_activity_count(self) -> int:
        """Return the count of the resident's recent activities."""
        return self.get_recent_activities().count()

    @property
    def activity_level(self):
        """Return a string indicating whether the resident is inactive, low,
        medium, or high activity.

        Based on the count of activities in the past seven days:
        - danger: 0-1
        - warning: 2-4
        - success: 5+
        """
        one_week_ago = timezone.now() - timezone.timedelta(days=7)
        activity_count: int = self.resident_activities.filter(  # type: ignore
            activity_date__gte=one_week_ago,
        ).count()

        color_class = None
        text = None

        if self.on_hiatus:
            color_class = "info"
            text = _("On hiatus")
        elif activity_count in WEEKLY_ACTIVITY_RANGES["inactive"]["range"]:
            color_class = WEEKLY_ACTIVITY_RANGES["inactive"]["color_class"]
            text = WEEKLY_ACTIVITY_RANGES["inactive"]["label"]
        elif activity_count in WEEKLY_ACTIVITY_RANGES["low"]["range"]:
            color_class = WEEKLY_ACTIVITY_RANGES["low"]["color_class"]
            text = WEEKLY_ACTIVITY_RANGES["low"]["label"]
        elif activity_count in WEEKLY_ACTIVITY_RANGES["good"]["range"]:
            color_class = WEEKLY_ACTIVITY_RANGES["good"]["color_class"]
            text = WEEKLY_ACTIVITY_RANGES["good"]["label"]
        else:
            color_class = WEEKLY_ACTIVITY_RANGES["high"]["color_class"]
            text = WEEKLY_ACTIVITY_RANGES["high"]["label"]

        return {
            "color_class": color_class,
            "text": text,
        }

    @property
    def current_residency(self):
        """Return the resident's current residency."""
        return self.residencies.get(move_out__isnull=True)

    @property
    def current_home(self):
        """Return the resident's current home."""
        return self.current_residency.home


class Residency(models.Model):
    resident = models.ForeignKey(
        to=Resident,
        on_delete=models.PROTECT,
        related_name="residencies",
    )
    home = models.ForeignKey(
        to=Home,
        on_delete=models.PROTECT,
    )
    move_in = models.DateField(
        default=timezone.now,
    )
    move_out = models.DateField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "residency"
        verbose_name = _("residency")
        verbose_name_plural = _("residencies")

    def __str__(self) -> str:
        return f"{self.resident.full_name} - {self.home.name}"

    def clean(self) -> None:
        """Ensure residency is valid.

        - move in date preceeds move out date, if present
        - resident should reside in only one home at a time (no residency overlap)
        """
        residency_timespan_is_valid = True

        if self.move_out:
            # Move in date is before move out (or on same date)
            residency_timespan_is_valid = self.move_in <= self.move_out

            # No residencies should exist for this resident
            # with overlapping move in/out dates (same date is fine)
            residency_has_overlap = Residency.objects.filter(
                resident=self.resident,
                move_in__lt=self.move_out,
                move_out__gt=self.move_in,
            ).exists()
        else:
            # No residencies should exist for this resident
            # with overlapping move out date (same date is fine)
            residency_has_overlap = Residency.objects.filter(
                resident=self.resident,
                move_out__gt=self.move_in,
            ).exists()

        if not residency_timespan_is_valid:
            error_message = _("Move-in date should preceed move-out date.")
            raise ValidationError(error_message)

        if residency_has_overlap:
            error_message = _("Resident can not have overlapping residencies.")
            raise ValidationError(error_message)

        return super().clean()
