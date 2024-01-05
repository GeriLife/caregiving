# import the forms module from django
from django import forms
from django.db.models import QuerySet
from residents.models import Residency
from .models import ResidentActivity
from django.contrib.auth import get_user_model

user_model = get_user_model()

activity_type_choices = [
    (choice[0], choice[1]) for choice in ResidentActivity.ActivityTypeChoices.choices
]
caregiver_role_choices = [
    (choice[0], choice[1]) for choice in ResidentActivity.CaregiverRoleChoices.choices
]


def group_residents_by_home(
    residencies: QuerySet[Residency],
) -> dict[str, list[tuple[int, str]]]:
    """Group residents by home.

    Args:
        residencies (QuerySet): A QuerySet of Residency objects with related 'home' and 'resident'.

    Returns:
        dict: A dictionary with home names as keys and a list of (resident_id, resident_name) tuples as values.
    """
    # Initialize a dictionary to group residents by home
    residents_by_home = {}

    for residency in residencies:
        home_name = residency.home.name
        resident_name = residency.resident.full_name  # Assuming full_name is a method

        if home_name not in residents_by_home:
            residents_by_home[home_name] = []

        residents_by_home[home_name].append((residency.resident.id, resident_name))

    # Sort residents by name within each home
    resident_name_col_index = 1
    for home in residents_by_home:
        residents_by_home[home].sort(
            key=lambda x: x[resident_name_col_index],
        )

    return residents_by_home


def prepare_resident_choices(residencies: QuerySet[Residency]) -> list[tuple[int, str]]:
    """Prepare a list of resident choices for a form.

    The list is sorted by home name and then by resident name.

    Args:
        residencies (QuerySet): A QuerySet of Residency objects with related 'home' and 'resident'.
    """
    residents_by_home = group_residents_by_home(residencies)

    # Sort the homes and convert the dictionary to the desired list format
    home_name_col_index = 0
    resident_choices = sorted(
        residents_by_home.items(),
        key=lambda x: x[home_name_col_index],
    )  # Sort by home name

    return resident_choices


def get_resident_choices(user=None):
    # Fetch Residency objects with related 'home' and 'resident' in a single query
    residencies = Residency.objects.filter(move_out__isnull=True).select_related(
        "home",
        "resident",
    )

    resident_choices = prepare_resident_choices(residencies)

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

    def __init__(self, user: user_model, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = kwargs.pop("user", None)

        self.fields["residents"].choices = get_resident_choices(user=user)
