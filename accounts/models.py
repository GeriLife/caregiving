from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models
from preferences.models import Preferences

class User(AbstractUser):
    class Meta:
        db_table = "user"
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.username

    #store user preferences in a one to one mapping
    preferences = models.OneToOneField(Preferences, on_delete=models.CASCADE, blank=True, null=True) 

    
