import factory

from activities.models import Activity
from .models import ResidentActivity


activity_type_choices = [choice[0] for choice in Activity.ActivityTypeChoices.choices]
caregiver_role_choices = [choice[0] for choice in Activity.CaregiverRoleChoices.choices]


class ResidentActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ResidentActivity

    resident = factory.SubFactory("residents.factories.ResidentFactory")
    activity = factory.SubFactory("activities.factories.ActivityFactory")
    activity_date = factory.Faker("date")
    residency = factory.SubFactory("residents.factories.ResidencyFactory")
    home = factory.SubFactory("homes.factories.HomeFactory")
    activity_type = factory.Faker(
        "random_element",
        elements=activity_type_choices,
    )
    activity_minutes = factory.Faker(
        "pyint",
        min_value=30,
        max_value=120,
    )
    caregiver_role = factory.Faker(
        "random_element",
        elements=caregiver_role_choices,
    )
