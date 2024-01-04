# import the forms module from django
from django import forms
from residents.models import Residency
from .models import ResidentActivity


activity_type_choices = [
    (choice[0], choice[1]) for choice in ResidentActivity.ActivityTypeChoices.choices
]
caregiver_role_choices = [
    (choice[0], choice[1]) for choice in ResidentActivity.CaregiverRoleChoices.choices
]


def get_resident_choices():
    # Fetch Residency objects with related 'home' and 'resident' in a single query
    residencies = Residency.objects.filter(move_out__isnull=True).select_related(
        "home",
        "resident",
    )

    # Initialize a dictionary to group residents by home
    resident_by_home = {}

    for residency in residencies:
        home_name = residency.home.name
        resident_name = residency.resident.full_name  # Assuming full_name is a method

        if home_name not in resident_by_home:
            resident_by_home[home_name] = []

        resident_by_home[home_name].append((residency.resident.id, resident_name))

    # Sort residents within each home
    resident_name_col_index = 1
    for home in resident_by_home:
        resident_by_home[home].sort(
            key=lambda x: x[resident_name_col_index],
        )  # Sort by resident name

    # Sort the homes and convert the dictionary to the desired list format
    home_name_col_index = 0
    resident_choices = sorted(
        resident_by_home.items(),
        key=lambda x: x[home_name_col_index],
    )  # Sort by home name
    return resident_choices


class ResidentActivityForm(forms.Form):
    """Form for creating a ResidentActivity instances."""

    residents = forms.MultipleChoiceField()
    activity_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"],
    )
    activity_type = forms.ChoiceField(choices=activity_type_choices)
    activity_minutes = forms.IntegerField()
    caregiver_role = forms.ChoiceField(choices=caregiver_role_choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["residents"].choices = get_resident_choices()
