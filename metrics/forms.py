# import the forms module from django
from django import forms
from residents.models import Resident
from .models import ResidentActivity


resident_choices = [
    (resident.id, resident.full_name)
    for resident in Resident.objects.filter(
        residency__isnull=False,
        residency__move_out__isnull=True,
    )
    .distinct()
    .order_by("first_name", "last_initial")
]
activity_type_choices = [
    (choice[0], choice[1]) for choice in ResidentActivity.ActivityTypeChoices.choices
]
caregiver_role_choices = [
    (choice[0], choice[1]) for choice in ResidentActivity.CaregiverRoleChoices.choices
]


class ResidentActivityForm(forms.Form):
    """Form for creating a ResidentActivity instances."""

    residents = forms.MultipleChoiceField(choices=resident_choices)
    activity_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"],
    )
    activity_type = forms.ChoiceField(choices=activity_type_choices)
    activity_minutes = forms.IntegerField()
    caregiver_role = forms.ChoiceField(choices=caregiver_role_choices)
