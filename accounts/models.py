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

        return Home.objects.filter(home_user_relations__user=self)

    @property
    def can_add_activity(self) -> bool:
        """Return True if the user can add an activity.

        A user can add an activity if they are a superuser or if they
        are associated with at least one home.
        """
        return self.is_superuser or self.homes.exists()

    def can_manage_residents(self, resident_ids: list[int]) -> bool:
        """Return True if the user can manage the residents.

        A user can manage the residents if they are a superuser or if
        they are associated with all of the residents' homes.
        """
        from residents.models import Resident
        from homes.models import HomeUserRelation

        if self.is_superuser:
            return True

        residents = Resident.objects.filter(id__in=resident_ids)

        for resident in residents:
            # Check if the user is associated with the resident's home
            if HomeUserRelation.objects.filter(
                home=resident.current_home,
                user=self,
            ).exists():
                return True

        return False
