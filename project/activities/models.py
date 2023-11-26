from django.db import models
from django.utils.translation import gettext_lazy as _


class ActivityType(models.Model):
    name = models.CharField(max_length=25)

    class Meta:
        db_table = "activity_type"
        verbose_name = _("activity type")
        verbose_name_plural = _("activity types")

    def __str__(self):
        return self.name


class Activity(models.Model):
    activity_type = models.ForeignKey(
        "ActivityType",
        on_delete=models.CASCADE,
        related_name="activities",
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
    duration_m = models.PositiveIntegerField(
        _("Duration in minutes"),
        default=30,
    )
    
    class Meta:
        db_table = "activity"
        verbose_name = _("activity")
        verbose_name_plural = _("activities")
        ordering = ["-date"]
