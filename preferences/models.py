from django.db import models

from django.utils.translation import gettext_lazy as _
from django.conf import settings

# for user preferences
class Preferences (models.Model):
    class LanguageTextChoices(TextChoices):
        ENGLISH = "english", _("English")
        SUOMI = "suomi", _("Suomi")
        
    class ColorModeTextChoices(TextChoices):
        DARK = "dark", _("Dark")
        LIGHT = "light", _("Light")
    
    language = models.CharField (max_length = 30, blank=True, choices=LanguageTextChoices)
    color_mode = models.CharField (max_length = 30, blank=True, choices=ColorModeTextChoices)
