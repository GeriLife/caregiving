from http import HTTPStatus
from django.test import TestCase

from .models import ResidentActivity
from homes.factories import HomeFactory, HomeUserRelationFactory
from residents.factories import ResidentFactory, ResidencyFactory
from datetime import date
from django.urls import reverse
from django.contrib.auth import get_user_model

user_model = get_user_model()


class ResidentActivityFormViewTestCase(TestCase):
    def setUp(self) -> None:
        # Create a user
        self.general_user = user_model.objects.create_user(
            username="gerneraluser",
            email="general@tzo.com",
            password="testpassword",
        )
        self.home_user = user_model.objects.create_user(
            username="testuser",
            email="test@email.com",
            password="testpassword",
        )
        self.superuser = user_model.objects.create_superuser(
            username="superuser",
            email="superuser@test.com",
            password="superuserpassword",
        )

        # Create test data using factories
        self.home1 = HomeFactory(name="Home 1")

        # Add the user to the home
        HomeUserRelationFactory(home=self.home1, user=self.home_user)

        # Create two residents
        self.resident1 = ResidentFactory(first_name="Alice")
        self.resident2 = ResidentFactory(first_name="Bob")

        # Create a residency for each resident
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

        self.url = reverse("resident-activity-form-view")

    def test_general_user_gets_403(self):
        """Test that a general user gets a 403 response."""
        # log in general user
        self.client.force_login(self.general_user)

        # Make GET request
        response = self.client.get(self.url)

        # The response should indicate a failure to process the form
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_home_user_gets_200(self):
        """Test that a home user gets a 200 response."""
        # log in home user
        self.client.force_login(self.home_user)

        # Make GET request
        response = self.client.get(self.url)

        # The response should indicate a successful form submission
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_superuser_gets_200(self):
        """Test that a superuser gets a 200 response."""
        # log in superuser
        self.client.force_login(self.superuser)

        # Make GET request
        response = self.client.get(self.url)

        # The response should indicate a successful form submission
        self.assertEqual(response.status_code, HTTPStatus.OK)

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
            "activity_type": ResidentActivity.ActivityTypeChoices.OUTDOOR,
            "activity_minutes": 30,
            "caregiver_role": ResidentActivity.CaregiverRoleChoices.NURSE,
        }

        # log in superuser
        self.client.force_login(self.superuser)

        # Make POST request
        response = self.client.post(
            self.url,
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
            "activity_type": ResidentActivity.ActivityTypeChoices.OUTDOOR,
            "activity_date": date.today(),
            "activity_minutes": 30,
            "caregiver_role": ResidentActivity.CaregiverRoleChoices.NURSE,
        }

        # log in superuser
        self.client.force_login(self.superuser)

        # Make POST request
        response = self.client.post(
            self.url,
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
