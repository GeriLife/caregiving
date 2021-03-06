from django.db import models
from django.utils.translation import gettext_lazy as _


class Home(models.Model):
    name = models.CharField(max_length=25)

    class Meta:
        db_table = "home"
        verbose_name = _("home")
        verbose_name_plural = _("homes")

    def __str__(self) -> str:
        return self.name
