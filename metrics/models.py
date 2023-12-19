from django.db import models
from django.utils.translation import gettext_lazy as _
from homes.models import Home
from residents.models import Resident
from activities.models import Activity
from residents.models import Residency


class ResidentActivity(models.Model):
    resident = models.ForeignKey(
        to=Resident,
        on_delete=models.PROTECT,
    )
    activity = models.ForeignKey(
        to=Activity,
        on_delete=models.PROTECT,
    )
    residency = models.ForeignKey(
        to=Residency,
        on_delete=models.PROTECT,
    )
    home = models.ForeignKey(
        Home,
        related_name="activity_performed",
        on_delete=models.CASCADE,
        help_text=_("The home in which this activity was performed"),
    )
    activity_type = models.CharField(
        _("Activity type"),
        max_length=20,
        choices=Activity.ActivityTypeChoices.choices,
        default=Activity.ActivityTypeChoices.SELF_GUIDED,
    )
    activity_minutes = models.PositiveIntegerField(
        _("Duration in minutes"),
        default=30,
    )
    activity_date = models.DateField(null=True, blank=True)
    caregiver_role = models.CharField(
        _("Caregiver role"),
        max_length=20,
        choices=Activity.CaregiverRoleChoices.choices,
        default=Activity.CaregiverRoleChoices.NURSE,
    )

    class Meta:
        db_table = "resident_activity"
        verbose_name = _("resident activity")
        verbose_name_plural = _("resident activities")
