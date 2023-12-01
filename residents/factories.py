import factory
import random
import string

from .models import Resident, Residency


class ResidentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Resident
        django_get_or_create = ("first_name", "last_initial")

    first_name: str = factory.Faker("first_name")
    # choose a random alphabetical character for the last initial
    last_initial = factory.LazyFunction(lambda: random.choice(string.ascii_uppercase))
    url_uuid: str = factory.Sequence(lambda n: f"url-uuid-{n}")


class ResidencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Residency
        django_get_or_create = ("resident", "home")

    resident = factory.SubFactory(ResidentFactory)
    home = factory.SubFactory("homes.factories.HomeFactory")
    move_in = factory.Faker("date")
    move_out = None
