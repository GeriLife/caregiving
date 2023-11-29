from django.db import models

def generate_lists (L):
    result = []
    for elem in L:
        result.append ((elem,elem))
    return result

languages = ['English (en)', 'Suomi (fi)']
viewModes = ['dark', 'light']

# for user preferences
class Preferences (models.Model):
    Language = models.CharField (max_length = 30, blank=True, choices = generate_lists (languages))
    Mode = models.CharField (max_length = 30, blank=True, choices = generate_lists (viewModes))