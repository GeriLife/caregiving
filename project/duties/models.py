from django.db import models

from caregivers.models import CaregiverRole
from homes.models import Home


class DutyType(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self) -> str:
        return self.name


class Duty(models.Model):
    home = models.ForeignKey(Home, related_name="duties_performed", on_delete=models.CASCADE)
    type = models.ForeignKey(DutyType, related_name="+", on_delete=models.PROTECT)
    caregiver_role = models.ForeignKey(CaregiverRole, related_name="+", on_delete=models.PROTECT)
    date = models.DateField()
    duration = models.PositiveIntegerField()
