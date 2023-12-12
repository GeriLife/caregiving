from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from homes.factories import Home
from django.core.management.base import CommandError


class MakeHomeTest(TestCase):
    def test_home_count(self):
        out = StringIO()
        call_command("make_fake_homes", 3, stdout=out)
        home_count = Home.objects.count()
        self.assertEqual(home_count, 3)
        self.assertIn("Created " + str(home_count) + " fake homes.", out.getvalue())

    def test_home_no_homes(self):
        out = StringIO()
        call_command("make_fake_homes", 0, stdout=out)
        home_count = Home.objects.count()
        self.assertEqual(home_count, 0)
        self.assertIn("Created " + str(home_count) + " fake homes.", out.getvalue())

    def test_home_negative_number(self):
        out = StringIO()
        call_command("make_fake_homes", -30, stdout=out)
        self.assertIn("Invalid n. Please try again.", out.getvalue())

    def test_home_invalid_string_number(self):
        out = StringIO()
        try:
            call_command("make_fake_homes", "two", stdout=out)
        except CommandError:
            home_count = Home.objects.count()
            self.assertEqual(home_count, 0)

    def test_home_invalid_string(self):
        try:
            out = StringIO()
            call_command("make_fake_homes", "hello", stdout=out)
        except CommandError:
            home_count = Home.objects.count()
            self.assertEqual(home_count, 0)

    def test_home_number_string_mix(self):
        try:
            out = StringIO()
            call_command("make_fake_homes", "hello", stdout=out)
        except CommandError:
            home_count = Home.objects.count()
            self.assertEqual(home_count, 0)
