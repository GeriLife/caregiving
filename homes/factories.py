import factory
from factory import Sequence


class HomeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "homes.Home"
        django_get_or_create = ("name",)

    name: str = Sequence(lambda n: f"Home {n}")
