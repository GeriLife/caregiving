from django.test import TestCase

from .factories import HomeFactory
from residents.factories import ResidentFactory, ResidencyFactory


class HomeModelTests(TestCase):
    def setUp(self):
        # Create test data using factories
        self.home1 = HomeFactory(name="Home 1")

        self.home_1_current_resident = ResidentFactory(first_name="Alice")
        self.home_1_past_resident = ResidentFactory(first_name="Bob")

        ResidencyFactory(
            resident=self.home_1_current_resident,
            home=self.home1,
            move_in="2020-01-01",
            move_out=None,
        )
        ResidencyFactory(
            resident=self.home_1_past_resident,
            home=self.home1,
            move_in="2020-01-02",
            move_out="2020-02-01",
        )

    def test_home_current_residencies(self):
        current_residencies_home1 = self.home1.current_residencies
        self.assertEqual(current_residencies_home1.count(), 1)
        self.assertTrue(
            current_residencies_home1.filter(
                resident=self.home_1_current_resident,
            ).exists(),
        )

    def test_home_current_residencies_exclude_past_residencies(self):
        # Testing Home 1
        current_residencies_home1 = self.home1.current_residencies
        self.assertFalse(
            current_residencies_home1.filter(
                resident=self.home_1_past_resident,
            ).exists(),
        )
