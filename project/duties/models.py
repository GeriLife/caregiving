from django.db import models
from django.utils.translation import gettext_lazy as _

from caregivers.models import CaregiverRole
from homes.models import Home


class DutyType(models.Model):
    name = models.CharField(max_length=25)

    class Meta:
        verbose_name = _("duty type")
        verbose_name_plural = _("duty types")

    def __str__(self) -> str:
        return self.name


class Duty(models.Model):
    home = models.ForeignKey(Home, related_name="duties_performed", on_delete=models.CASCADE, help_text=_("The home in which this duty was performed."))
    type = models.ForeignKey(DutyType, related_name="+", on_delete=models.PROTECT, help_text=_("The general type of task or duty performed."))
    caregiver_role = models.ForeignKey(CaregiverRole, related_name="+", on_delete=models.PROTECT, help_text=_("The role or job title of the person who performed this duty."))
    date = models.DateField(help_text=_("The date this duty was performed."))
    duration = models.PositiveIntegerField(help_text=_("The number of minutes used performing this duty."))

    class Meta:
        verbose_name = _("duty")
        verbose_name_plural = _("duties")

    def __str__(self):
        return f"{ self.home } - { self.caregiver_role } - { self.type } - { self.date } - { self.duration }"
