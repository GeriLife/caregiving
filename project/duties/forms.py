from django import forms

from .models import Duty


class DutyForm(forms.ModelForm):
    class Meta:
        model = Duty
        fields = "__all__"
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
