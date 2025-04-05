import factory
from factory import Sequence
import datetime

from caregivers.factories import CaregiverRoleFactory
from homes.factories import HomeFactory
from .models import Work, WorkType


class WorkTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkType
        django_get_or_create = ("name",)

    name = Sequence(lambda n: f"Work Type {n}")


class WorkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Work

    home = factory.SubFactory(HomeFactory)
    type = factory.SubFactory(WorkTypeFactory)
    caregiver_role = factory.SubFactory(CaregiverRoleFactory)
    date = factory.LazyFunction(datetime.date.today)
    duration_minutes = factory.Faker("random_int", min=15, max=480)
