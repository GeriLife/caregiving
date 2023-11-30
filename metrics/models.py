from django.db import models
from django.utils.translation import gettext_lazy as _
from homes.models import Home
from residents.models import Resident
from activities.models import Activity
from residents.models import Residency
from django.db.models.signals import post_save
from django.dispatch import receiver


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
        choices=Activity.ActivityTypeChoices.choices,
        default=Activity.ActivityTypeChoices.SELF_GUIDED,
    )
    activity_minutes = models.PositiveIntegerField(
        _("Duration in minutes"),
        default=30,
    )
    caregiver_role = models.CharField(
        _("Caregiver role"),
        max_length=20,
        choices=Activity.CaregiverRoleChoices.choices,
        default=Activity.CaregiverRoleChoices.STAFF,
    )

    class Meta:
        db_table = "resident_activity"
        verbose_name = _("resident_activity")
        verbose_name_plural = _("resident_activities")

    @receiver(post_save, sender=Activity)
    def add_resident_activity(sender, instance, **kwargs):
        residents = instance.residents.all().values_list("Resident", flat=True)
        for r in residents:
            resident = r
            activity = instance.id
            cur_residency = Residency.objects.filter(
                resident=r,
                move_out__isnull=True,
            )
            residency = cur_residency.id
            home = cur_residency.home.id
            activity_type = instance.activity_type
            activity_minutes = instance.duration_minutes
            caregiver_role = instance.caregiver_role

            resident_activity = ResidentActivity.objects.create(
                resident=resident,
                activity=activity,
                residency=residency,
                home=home,
                activity_type=activity_type,
                activity_minutes=activity_minutes,
                caregiver_role=caregiver_role,
            )
            resident_activity.save()
