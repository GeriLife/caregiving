from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from residents.factories import Residency
from django.core.management.base import CommandError


class MakeresidencyTest(TestCase):
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
