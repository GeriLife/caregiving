import factory
from factory import Sequence

from .models import CaregiverRole


class CaregiverRoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CaregiverRole
        django_get_or_create = ("name",)

    name = Sequence(lambda n: f"Caregiver Role {n}")
