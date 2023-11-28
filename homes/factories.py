import factory
from .models import Home


class HomeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Home
        django_get_or_create = ("name",)

    name: str = factory.Sequence(lambda n: f"Home {n}")
