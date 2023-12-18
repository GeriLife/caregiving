from http import HTTPStatus
from django.test import TestCase

from activities.models import Activity
from .models import ResidentActivity
from homes.factories import HomeFactory
from residents.factories import ResidentFactory, ResidencyFactory
from datetime import date
from django.urls import reverse


class ResidentActivityTestCase(TestCase):
    def setUp(self):
        # Create test data using factories
        self.home1 = HomeFactory(name="Home 1")
        self.resident1 = ResidentFactory(first_name="Alice")
        self.resident2 = ResidentFactory(first_name="Bob")
        self.residency1 = ResidencyFactory(
            home=self.home1,
            resident=self.resident1,
            move_out=None,
        )
        self.residency2 = ResidencyFactory(
            home=self.home1,
            resident=self.resident2,
            move_out=None,
        )

    def test_initial_resident_activity(self):
        """Initially no resident activity."""
        initial_resident_activity = ResidentActivity.objects.filter(
            home=self.home1,
        ).count()
        self.assertEqual(initial_resident_activity, 0)

    def test_add_activity_adds_resident_activity(self):
        """When activity is added, resident activity is added."""
        # activity count pre
        activity_count_pre = Activity.objects.all().count()
        # pre count
        resident_activity_count_pre = ResidentActivity.objects.all().count()

        self.data = {
            "residents": [self.resident1.id],
            "activity_type": Activity.ActivityTypeChoices.OUTDOOR,
            # get the current date
            "date": date.today(),
            "duration_minutes": 30,
            "caregiver_role": Activity.CaregiverRoleChoices.NURSE,
        }
        response = self.client.post(
            reverse("activity-form-view"),
            self.data,
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # activity count post
        activity_count_post = Activity.objects.all().count()

        expected_activity_count_post = 1

        self.assertEqual(activity_count_post, expected_activity_count_post)

        # ResidentActivity post count
        resident_activity_count_post = ResidentActivity.objects.all().count()

        expected_resident_activity_count_post = 1

        self.assertEqual(
            resident_activity_count_post,
            expected_resident_activity_count_post,
        )

        # Activity pre count should be less than post count
        self.assertLess(activity_count_pre, activity_count_post)

        # ResidentActivity pre count should be less than post count
        self.assertLess(resident_activity_count_pre, resident_activity_count_post)
