from django.db import models
from django.utils.translation import gettext_lazy as _

from caregivers.models import CaregiverRole
from core.constants import HOUR_MINUTES
from homes.models import Home


class WorkType(models.Model):
    name = models.CharField(max_length=25)

    class Meta:
        db_table = "work_type"
        verbose_name = _("work type")
        verbose_name_plural = _("work types")

    def __str__(self) -> str:
        return self.name


class Work(models.Model):
    home = models.ForeignKey(
        Home,
        related_name="work_performed",
        on_delete=models.CASCADE,
        help_text=_("The home in which this work was performed"),
    )
    type = models.ForeignKey(
        WorkType,
        related_name="+",
        on_delete=models.PROTECT,
        help_text=_("The general type of work performed"),
    )
    caregiver_role = models.ForeignKey(
        CaregiverRole,
        related_name="+",
        on_delete=models.PROTECT,
        help_text=_("The role or job title of the person who performed this work"),
    )
    date = models.DateField(help_text=_("The date this work was performed"))
    duration_minutes = models.PositiveIntegerField(
        help_text=_("The number of minutes used performing this work"),
    )

    class Meta:
        db_table = "work"
        verbose_name = _("work")
        verbose_name_plural = _("work")

    def get_duration_hours(self):
        return self.duration_minutes / HOUR_MINUTES

    def save(self, *args, **kwargs):
        self.duration_hours = self.get_duration_hours()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{ self.home } - { self.caregiver_role } - { self.type } - { self.date } - { self.duration }"
