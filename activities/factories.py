from datetime import timedelta
import random
import factory
from django.utils import timezone

from residents.models import Resident
from residents.factories import ResidentFactory

from .models import Activity

activity_type_choices = [choice[0] for choice in Activity.ActivityTypeChoices.choices]
caregiver_role_choices = [choice[0] for choice in Activity.CaregiverRoleChoices.choices]


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Activity

    activity_type = factory.Faker("random_element", elements=activity_type_choices)
    date = factory.LazyFunction(
        lambda: timezone.now().date() - timedelta(days=random.randint(0, 30)),
    )
    duration_minutes = factory.Faker("pyint", min_value=30, max_value=120)
    caregiver_role = factory.Faker("random_element", elements=caregiver_role_choices)

    @factory.post_generation
    def residents(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # A list of residents were passed in, use them
            for resident in extracted:
                self.residents.add(resident)
        else:
            # Try to get an existing resident
            existing_residents = Resident.objects.all()
            if existing_residents:
                random_resident = random.choice(existing_residents)
                self.residents.add(random_resident)
            else:
                # No existing residents, create a new one
                resident = ResidentFactory()
                self.residents.add(resident)
