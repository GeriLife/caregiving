from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from shortuuid.django_fields import ShortUUIDField
from homes.models import Home


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
