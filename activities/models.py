from django.db import models
from django.utils.translation import gettext_lazy as _


class Activity(models.Model):
    """Model representing an activity."""

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

    activity_type = models.CharField(
        _("Activity type"),
        max_length=20,
        choices=ActivityTypeChoices.choices,
        default=ActivityTypeChoices.SELF_GUIDED,
    )
    residents = models.ManyToManyField(
        "residents.Resident",
        related_name="activities",
    )
    date = models.DateField(
        _("Activity date"),
        auto_now=False,
        auto_now_add=False,
    )
    duration_minutes = models.PositiveIntegerField(
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
        db_table = "activity"
        verbose_name = _("activity")
        verbose_name_plural = _("activities")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.activity_type} activity on {self.date}"
