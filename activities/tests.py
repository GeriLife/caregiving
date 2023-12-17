# Create your tests here.
from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from activities.factories import Activity
from django.core.management.base import CommandError


class MakeFakeActivityTest(TestCase):
    def test_activity_count(self):
        out = StringIO()
        call_command("make_fake_activities", 3, stdout=out)
        activity_count = Activity.objects.count()
        self.assertEqual(activity_count, 3)
        self.assertIn(
            "Created " + str(activity_count) + " fake activities.",
            out.getvalue(),
        )

    def test_activity_no_activities(self):
        out = StringIO()
        call_command("make_fake_activities", 0, stdout=out)
        activity_count = Activity.objects.count()
        self.assertEqual(activity_count, 0)
        self.assertIn(
            "Created " + str(activity_count) + " fake activities.",
            out.getvalue(),
        )

    def test_activity_negative_number(self):
        out = StringIO()
        call_command("make_fake_activities", -30, stdout=out)
        self.assertIn("Invalid n. Please try again.", out.getvalue())

    def test_activity_invalid_string_number(self):
        out = StringIO()
        try:
            call_command("make_fake_activities", "two", stdout=out)
        except CommandError:
            activity_count = Activity.objects.count()
            self.assertEqual(activity_count, 0)

    def test_activity_invalid_string(self):
        try:
            out = StringIO()
            call_command("make_fake_activities", "hello", stdout=out)
        except CommandError:
            activity_count = Activity.objects.count()
            self.assertEqual(activity_count, 0)

    def test_activity_number_string_mix(self):
        try:
            out = StringIO()
            call_command("make_fake_activities", "hello", stdout=out)
        except CommandError:
            activity_count = Activity.objects.count()
            self.assertEqual(activity_count, 0)
