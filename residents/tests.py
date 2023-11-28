from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import MagicMock, patch

from .models import Residency, Resident
from homes.models import Home


class ResidencyTestCase(TestCase):
    def setUp(self):
        self.resident = Resident.objects.create(
            first_name="Test",
            last_initial="U",
        )
        self.home = Home.objects.create(
            name="Test Home",
        )

    def test_residency_dates_are_valid(self):
        """Creating a residency where the move out date is before move in
        should raise a validation error."""
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
        """Residents should only live in one home at a time so overlapping
        residencies should not be allowed."""

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


class TestResidentActivityLevel(TestCase):
    def setUp(self):
        self.resident = Resident.objects.create(first_name="John", last_initial="W")

    def test_activity_levels(self):
        expected_results = {
            0: {"color": "danger", "text": "Inactive"},
            1: {"color": "warning", "text": "Low"},
            2: {"color": "warning", "text": "Low"},
            3: {"color": "warning", "text": "Low"},
            4: {"color": "warning", "text": "Low"},
            5: {"color": "success", "text": "Moderate"},
            6: {"color": "success", "text": "Moderate"},
            7: {"color": "success", "text": "Moderate"},
            8: {"color": "success", "text": "Moderate"},
            9: {"color": "success", "text": "Moderate"},
            10: {"color": "warning", "text": "High"},
            11: {"color": "warning", "text": "High"},
            12: {"color": "warning", "text": "High"},
            13: {"color": "warning", "text": "High"},
            14: {"color": "warning", "text": "High"},
        }

        for count in range(0, 15):
            with self.subTest(count=count):
                with patch(
                    "residents.models.Resident.activities",
                    new_callable=MagicMock,
                ) as mock_activities:
                    # Set up the method chain to return the correct count
                    mock_activities.filter.return_value.count.return_value = count

                    # Test the actual functionality
                    expected = expected_results.get(count)
                    self.assertEqual(self.resident.activity_level, expected)

    def test_on_hiatus(self):
        self.resident.on_hiatus = True
        expected = {"color": "info", "text": "On hiatus"}
        self.assertEqual(self.resident.activity_level, expected)
