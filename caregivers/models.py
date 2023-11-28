from django.db import models
from django.utils.translation import gettext_lazy as _


class CaregiverRole(models.Model):
    name = models.CharField(max_length=25)

    class Meta:
        db_table = "caregiver_role"
        verbose_name = _("caregiver role")
        verbose_name_plural = _("caregiver roles")

    def __str__(self) -> str:
        return self.name
