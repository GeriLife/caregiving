from http import HTTPStatus
from django.test import TestCase

from activities.models import Activity
from .models import ResidentActivity
from homes.factories import HomeFactory
from residents.factories import ResidentFactory, ResidencyFactory
from datetime import date
from django.urls import reverse


class ResidentActivityFormViewTestCase(TestCase):
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

    def test_resident_activity_form_view_create_multiple_resident_activity(self):
        """Test that multiple resident activities can be created with one POST
        request."""
        # Count of activities and resident activities before POST request
        resident_activity_count_pre = ResidentActivity.objects.all().count()

        activity_residents = [self.resident1.id, self.resident2.id]
        # Prepare data for POST request
        self.data = {
            "residents": activity_residents,
            "activity_date": date.today(),
            "activity_type": Activity.ActivityTypeChoices.OUTDOOR,
            "activity_minutes": 30,
            "caregiver_role": Activity.CaregiverRoleChoices.NURSE,
        }

        # Make POST request
        response = self.client.post(
            reverse("resident-activity-form-view"),
            self.data,
        )

        # The response should indicate a successful form submission
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Count of activities and resident activities after POST request
        resident_activity_count_post = ResidentActivity.objects.all().count()

        self.assertLess(
            resident_activity_count_pre,
            resident_activity_count_post,
        )

        expected_resident_activity_count = len(activity_residents)

        # Ensure counts have increased by 2
        self.assertEqual(
            resident_activity_count_post,
            expected_resident_activity_count,
        )

    def test_initial_resident_activity(self):
        """Initially no resident activity."""
        initial_resident_activity = ResidentActivity.objects.filter(
            home=self.home1,
        ).count()
        self.assertEqual(initial_resident_activity, 0)

    def test_activity_rollback_on_residency_exception(self):
        """Activity and ResidentActivity are not added if
        Residency.DoesNotExist exception is raised."""
        # This person does not have a residency
        non_resident = ResidentFactory(first_name="Charlie")

        # Count of activities and resident activities before POST request
        resident_activity_count_pre = ResidentActivity.objects.all().count()

        # Prepare data for POST request with a resident that does not have a residency
        self.data = {
            "residents": [non_resident.id],
            "activity_type": Activity.ActivityTypeChoices.OUTDOOR,
            "activity_date": date.today(),
            "activity_minutes": 30,
            "caregiver_role": Activity.CaregiverRoleChoices.NURSE,
        }

        # Make POST request
        response = self.client.post(
            reverse("resident-activity-form-view"),
            self.data,
        )

        # The response should indicate a failure to process the form
        self.assertNotEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Form should not be valid
        self.assertFalse(response.context["form"].is_valid())

        # form should have errors
        self.assertTrue(response.context["form"].errors)

        # form errors should include residency error
        self.assertTrue(response.context["form"].errors["residents"])

        # Since there is no residency for the resident, the form should not be valid
        # i.e., the resident ID is not a valid choice
        self.assertIn("Select a valid choice.", str(response.context["form"].errors))

        # Count of activities and resident activities after POST request
        resident_activity_count_post = ResidentActivity.objects.all().count()

        # Ensure counts have not changed, indicating a rollback
        self.assertEqual(resident_activity_count_pre, resident_activity_count_post)
