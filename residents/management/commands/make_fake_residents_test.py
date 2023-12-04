from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from residents.factories import Resident
from django.core.management.base import CommandError


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
