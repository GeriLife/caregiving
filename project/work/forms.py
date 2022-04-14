from django import forms

from .models import Work


class WorkForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = "__all__"
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
