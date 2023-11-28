from django.test import TestCase

from .factories import HomeFactory
from residents.factories import ResidentFactory, ResidencyFactory


class HomeModelTests(TestCase):
    def setUp(self):
        # Create test data using factories
        self.home1 = HomeFactory(name="Home 1")
        self.home2 = HomeFactory(name="Home 2")

        self.resident1 = ResidentFactory(first_name="Alice")
        self.resident2 = ResidentFactory(first_name="Bob")
        self.resident3 = ResidentFactory(first_name="Charlie")

        ResidencyFactory(
            resident=self.resident1,
            home=self.home1,
            move_in="2020-01-01",
            move_out=None,
        )
        ResidencyFactory(
            resident=self.resident2,
            home=self.home1,
            move_in="2020-01-02",
            move_out="2020-02-01",
        )
        ResidencyFactory(
            resident=self.resident3,
            home=self.home2,
            move_in="2020-01-03",
            move_out=None,
        )

    def test_home_current_residencies(self):
        # Testing Home 1
        current_residencies_home1 = self.home1.current_residencies
        self.assertEqual(current_residencies_home1.count(), 1)
        self.assertTrue(
            current_residencies_home1.filter(resident=self.resident1).exists(),
        )

        # Testing Home 2
        current_residencies_home2 = self.home2.current_residencies
        self.assertEqual(current_residencies_home2.count(), 1)
        self.assertTrue(
            current_residencies_home2.filter(resident=self.resident3).exists(),
        )

    def test_home_current_residencies_exclude_past_residencies(self):
        # Testing Home 1
        current_residencies_home1 = self.home1.current_residencies
        self.assertFalse(
            current_residencies_home1.filter(resident=self.resident2).exists(),
        )

        # Testing Home 2
        current_residencies_home2 = self.home2.current_residencies
        self.assertFalse(
            current_residencies_home2.filter(resident=self.resident1).exists(),
        )
