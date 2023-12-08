from django import forms
from django.forms import ModelForm
from preferences.models import Preferences

class PreferencesForm (ModelForm):
    class Meta:
        model = Preferences
        fields = ('Language', 'Mode')
        widgets = {
            'Language': forms.Select(attrs={'class': 'form-control'}),
            'Mode': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {'Language': 'Preferred Language',
                  'Mode': 'Preferred Mode'}