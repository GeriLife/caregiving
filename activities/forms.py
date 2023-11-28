from django import forms

from .models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = "__all__"
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
