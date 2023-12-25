from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from django.core.management.base import CommandError

from django.core.exceptions import ValidationError
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
            0: {"color_class": "danger", "text": "Inactive"},
            1: {"color_class": "warning", "text": "Low"},
            2: {"color_class": "warning", "text": "Low"},
            3: {"color_class": "warning", "text": "Low"},
            4: {"color_class": "warning", "text": "Low"},
            5: {"color_class": "success", "text": "Moderate"},
            6: {"color_class": "success", "text": "Moderate"},
            7: {"color_class": "success", "text": "Moderate"},
            8: {"color_class": "success", "text": "Moderate"},
            9: {"color_class": "success", "text": "Moderate"},
            10: {"color_class": "warning", "text": "High"},
            11: {"color_class": "warning", "text": "High"},
            12: {"color_class": "warning", "text": "High"},
            13: {"color_class": "warning", "text": "High"},
            14: {"color_class": "warning", "text": "High"},
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
        expected = {"color_class": "info", "text": "On hiatus"}
        self.assertEqual(self.resident.activity_level, expected)


class MakeResidencyTest(TestCase):
    def test_residency_count(self):
        out = StringIO()
        call_command("make_fake_residencies", 3, stdout=out)
        residency_count = Residency.objects.count()
        self.assertEqual(residency_count, 3)
        self.assertIn(
            "Created " + str(residency_count) + " fake residencies.",
            out.getvalue(),
        )

    def test_residency_no_residencies(self):
        out = StringIO()
        call_command("make_fake_residencies", 0, stdout=out)
        residency_count = Residency.objects.count()
        self.assertEqual(residency_count, 0)
        self.assertIn(
            "Created " + str(residency_count) + " fake residencies.",
            out.getvalue(),
        )

    def test_residency_negative_number(self):
        out = StringIO()
        call_command("make_fake_residencies", -30, stdout=out)
        self.assertIn("Invalid n. Please try again.", out.getvalue())

    def test_residency_invalid_string_number(self):
        out = StringIO()
        try:
            call_command("make_fake_residencies", "two", stdout=out)
        except CommandError:
            residency_count = Residency.objects.count()
            self.assertEqual(residency_count, 0)

    def test_residency_invalid_string(self):
        try:
            out = StringIO()
            call_command("make_fake_residencies", "hello", stdout=out)
        except CommandError:
            residency_count = Residency.objects.count()
            self.assertEqual(residency_count, 0)

    def test_residency_number_string_mix(self):
        try:
            out = StringIO()
            call_command("make_fake_residencies", "hello", stdout=out)
        except CommandError:
            residency_count = Residency.objects.count()
            self.assertEqual(residency_count, 0)


class MakeResidentTest(TestCase):
    def test_resident_count(self):
        out = StringIO()
        call_command("make_fake_residents", 3, stdout=out)
        resident_count = Resident.objects.count()
        self.assertEqual(resident_count, 3)
        self.assertIn(
            "Created " + str(resident_count) + " fake residents.",
            out.getvalue(),
        )

    def test_resident_no_residents(self):
        out = StringIO()
        call_command("make_fake_residents", 0, stdout=out)
        resident_count = Resident.objects.count()
        self.assertEqual(resident_count, 0)
        self.assertIn(
            "Created " + str(resident_count) + " fake residents.",
            out.getvalue(),
        )

    def test_resident_negative_number(self):
        out = StringIO()
        call_command("make_fake_residents", -30, stdout=out)
        self.assertIn("Invalid n. Please try again.", out.getvalue())

    def test_resident_invalid_string_number(self):
        out = StringIO()
        try:
            call_command("make_fake_residents", "two", stdout=out)
        except CommandError:
            resident_count = Resident.objects.count()
            self.assertEqual(resident_count, 0)

    def test_resident_invalid_string(self):
        try:
            out = StringIO()
            call_command("make_fake_residents", "hello", stdout=out)
        except CommandError:
            resident_count = Resident.objects.count()
            self.assertEqual(resident_count, 0)

    def test_resident_number_string_mix(self):
        try:
            out = StringIO()
            call_command("make_fake_residents", "hello", stdout=out)
        except CommandError:
            resident_count = Resident.objects.count()
            self.assertEqual(resident_count, 0)
