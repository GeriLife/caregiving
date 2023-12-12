from typing import TYPE_CHECKING
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from shortuuid.django_fields import ShortUUIDField

if TYPE_CHECKING:
    from residents.models import Resident


class Home(models.Model):
    name = models.CharField(max_length=25)
    # add a foreign key relationship to HomeGroup
    home_group = models.ForeignKey(
        to="homes.HomeGroup",
        on_delete=models.PROTECT,
        related_name="homes",
        null=True,
        blank=True,
    )

    url_uuid = ShortUUIDField(
        _("UUID used in URLs"),
        editable=False,  # type: ignore
    )

    class Meta:
        db_table = "home"
        verbose_name = _("home")
        verbose_name_plural = _("homes")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("home-detail-view", kwargs={"url_uuid": self.url_uuid})

    @property
    def current_residents(self) -> models.QuerySet["Resident"]:
        """Returns a QuerySet of all current residents for this home."""
        # avoid circular import
        from residents.models import Resident

        return Resident.objects.filter(
            residency__home=self,
            residency__move_out__isnull=True,
        ).order_by("first_name")


class HomeGroup(models.Model):
    name = models.CharField(max_length=25)

    url_uuid = ShortUUIDField(
        _("UUID used in URLs"),
        editable=False,  # type: ignore
    )

    class Meta:
        db_table = "home_group"
        verbose_name = _("home group")
        verbose_name_plural = _("home groups")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("home-group-detail-view", kwargs={"url_uuid": self.url_uuid})
