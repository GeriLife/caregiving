from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from shortuuid.django_fields import ShortUUIDField
from homes.models import Home


# Activity ranges
#
# Based on the count of activities in the past seven days:
# - inactive: almost no activities
# - low: a few activities
# - good: an appropriate amount of activities
# - high: a lot of activities (maybe too many)
#
# Note: range ends are exclusive, so the max value is the same as the next
# range's min value.
WEEKLY_ACTIVITY_RANGES = {
    "inactive": range(0, 1),  # Includes only 0.
    "low": range(1, 5),  # Includes 1, 2, 3, 4.
    "good": range(5, 10),  # Includes 5, 6, 7, 8, 9.
    "high": range(10, 1000),  # Includes 10 onwards ... (1000 is arbitrary).
}


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
        return f"{ self.first_name } { self.last_initial }"

    class Meta:
        db_table = "resident"
        verbose_name = _("resident")
        verbose_name_plural = _("residents")

    def __str__(self) -> str:
        return self.full_name

    def get_absolute_url(self):
        return reverse("resident-detail-view", kwargs={"url_uuid": self.url_uuid})

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
        activity_count: int = self.activities.filter(  # type: ignore
            date__gte=one_week_ago,
        ).count()

        if self.on_hiatus:
            return {
                "color": "info",
                "text": _("On hiatus"),
            }
        elif activity_count in WEEKLY_ACTIVITY_RANGES["inactive"]:
            return {
                "color": "danger",
                "text": _("Inactive"),
            }
        elif activity_count in WEEKLY_ACTIVITY_RANGES["low"]:
            return {
                "color": "warning",
                "text": _("Low"),
            }
        elif activity_count in WEEKLY_ACTIVITY_RANGES["good"]:
            return {
                "color": "success",
                "text": _("Moderate"),
            }
        else:
            return {
                "color": "warning",
                "text": _("High"),
            }


class Residency(models.Model):
    resident = models.ForeignKey(
        to=Resident,
        on_delete=models.PROTECT,
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
        return f"{ self.resident.full_name } - { self.home.name }"

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
