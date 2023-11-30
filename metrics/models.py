from django.db import models
from django.utils.translation import gettext_lazy as _
from homes.models import Home
from residents.models import Resident
from activities.models import Activity
from activities.models import CaregiverRoleChoices
from activities.models import ActivityTypeChoices
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
        to=Home,
        on_delete=models.PROTECT,
    )
    activity_type = models.CharField(
        _("Activity type"),
        max_length=20,
        choices=ActivityTypeChoices.choices,
        default=ActivityTypeChoices.SELF_GUIDED,
    )
    activity_minutes = models.PositiveIntegerField(
        _("Duration in minutes"),
        default=30,
    )
    caregiver_role = models.CharField(
        _("Caregiver role"),
        max_length=20,
        choices=CaregiverRoleChoices.choices,
        default=CaregiverRoleChoices.STAFF,
    )

    class Meta:
        db_table = "resident_activity"
        verbose_name = _("resident_activity")
        verbose_name_plural = _("resident_activities")
