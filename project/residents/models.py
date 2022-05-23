import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Resident(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_initial = models.CharField(max_length=1)
    on_hiatus = models.BooleanField(default=False)

    def full_name(self):
        return f"{ self.first_name } { self.last_initial }"

    class Meta:
        db_table = "resident"
        verbose_name = _("resident")
        verbose_name_plural = _("residents")

    def __str__(self) -> str:
        return self.full_name()
