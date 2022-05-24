from datetime import datetime
import uuid
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from homes.models import Home


class Resident(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_initial = models.CharField(max_length=1)
    on_hiatus = models.BooleanField(default=False)

    @property
    def full_name(self):
        return f"{ self.first_name } { self.last_initial }"

    class Meta:
        db_table = "resident"
        verbose_name = _("resident")
        verbose_name_plural = _("residents")

    def __str__(self) -> str:
        return self.full_name

    def get_absolute_url(self):
        return reverse("resident-detail", kwargs={"pk": self.pk})


class Residency(models.Model):
    resident = models.ForeignKey(
        to=Resident,
        on_delete=models.PROTECT,
    )
    home = models.ForeignKey(
        to=Home,
        on_delete=models.PROTECT,
    )
    move_in = models.DateField(
        default=timezone.now,
    )
    move_out = models.DateField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "residency"
        verbose_name = _("residency")
        verbose_name_plural = _("residencies")

    def __str__(self) -> str:
        return f"{ self.resident.full_name } - { self.home.name }"
