from django.core.exceptions import ValidationError
from django.test import TestCase
from psycopg2 import Date

from .models import Residency, Resident
from homes.models import Home

class ResidencyTestCase(TestCase):
    def setUp(self):
        self.resident = Resident.objects.create(
            first_name="Test",
            last_initial="U"
        )
        self.home = Home.objects.create(
            name="Test Home"
        )

    def test_residency_dates_are_valid(self):
        """
        Creating a residency where the move out date is before move in
        should raise a validation error
        """
        with self.assertRaises(ValidationError):
            residency = Residency.objects.create(
                resident=self.resident,
                home=self.home,
                move_in="2022-03-02",
                # Move out is before move in
                # so should raise validation error
                move_out="2022-03-01",
            )

            # We need to manually call the clean() method
            # since it is not automatically called when
            # saving a model instance
            # https://docs.djangoproject.com/en/4.0/ref/models/instances/#django.db.models.Model.clean
            residency.clean()

    def test_overlapping_residency_not_allowed(self):
        """
        Residents should only live in one home at a time
        so overlapping residencies should not be allowed
        """

        with self.assertRaises(ValidationError):
            # Create a residency that will overlap with the new residency
            Residency.objects.create(
                resident=self.resident,
                home=self.home,
                move_in="2022-03-01",
                move_out="2022-03-10",
            )

            # Create a residency that overlaps with the previous residency
            overlapping_residency = Residency.objects.create(
                resident=self.resident,
                home=self.home,
                move_in="2022-03-05",
                move_out="2022-03-20",
            )

            # We need to manually call the clean() method
            # since it is not automatically called when
            # saving a model instance
            # https://docs.djangoproject.com/en/4.0/ref/models/instances/#django.db.models.Model.clean
            overlapping_residency.clean()
