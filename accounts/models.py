from django.db.models import QuerySet
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Meta:
        db_table = "user"
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.username

    def get_full_name(self) -> str:
        return self.first_name + " " + self.last_name

    @property
    def homes(self) -> QuerySet["homes.Home"]:
        from homes.models import Home

        return Home.objects.filter(homeuserrelation__user=self)
