import factory
from factory import Sequence

from .models import Home, HomeGroup, HomeUserRelation


class HomeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Home
        django_get_or_create = ("name",)

    name: str = Sequence(lambda n: f"Home {n}")


class HomeGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HomeGroup
        django_get_or_create = ("name",)

    name: str = Sequence(lambda n: f"Home Group {n}")


class HomeUserRelationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HomeUserRelation
        django_get_or_create = ("home", "user")

    home: Home = factory.SubFactory(HomeFactory)
    user: Home = factory.SubFactory(HomeFactory)
