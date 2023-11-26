from django.db import models
from django.utils.translation import gettext_lazy as _


class Activity(models.Model):
    """
    Model representing an activity.
    """
    class ActivityTypeChoices(models.TextChoices):
        """
        Choices for the type of activity.
        """
        OUTDOOR = "outdoor", _("Outdoor")
        CULTURE = "culture", _("Culture")
        DISCUSSION = "discussion", _("Discussion")
        SELF_GUIDED = "self_guided", _("Self-guided")

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
    
    class Meta:
        db_table = "activity"
        verbose_name = _("activity")
        verbose_name_plural = _("activities")
        ordering = ["-date"]
