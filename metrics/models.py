from django.db import models
from django.utils.translation import gettext_lazy as _
from homes.models import Home
from residents.models import Resident
from residents.models import Residency


class ResidentActivity(models.Model):
    class ActivityTypeChoices(models.TextChoices):
        """Choices for the type of activity."""

        OUTDOOR = "outdoor", _("Outdoor")
        CASUAL_SOCIAL = "casual_social", _("Casual Social")
        CULTURE = "culture", _("Culture")
        DISCUSSION = "discussion", _("Discussion")
        GUIDED = "guided", _("Guided")
        MUSIC = "music", _("Music")
        SELF_GUIDED = "self_guided", _("Self-guided")
        TRIP = "trip", _("Trip")

    class CaregiverRoleChoices(models.TextChoices):
        """Choices for the caregiver role."""

        FAMILY = "family", _("Family")
        FRIEND = "friend", _("Friend")
        HOBBY_INSTRUCTOR = "hobby_instructor", _("Hobby Instructor")
        NURSE = "nurse", _("Nurse")
        PHYSIO_THERAPIST = "physio_therapist", _("Physio therapist")
        PRACTICAL_NURSE = "practical_nurse", _("Practical nurse")
        VOLUNTEER = "volunteer", _("Volunteer")

    resident = models.ForeignKey(
        to=Resident,
        on_delete=models.PROTECT,
        related_name="resident_activities",
    )
    activity_date = models.DateField(
        _("Activity date"),
        auto_now=False,
        auto_now_add=False,
        null=True,
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
        default=CaregiverRoleChoices.NURSE,
    )

    class Meta:
        db_table = "resident_activity"
        verbose_name = _("resident_activity")
        verbose_name_plural = _("resident_activities")
