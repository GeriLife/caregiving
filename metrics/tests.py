from http import HTTPStatus
from django.test import TestCase

from metrics.forms import group_residents_by_home, prepare_resident_choices
from residents.models import Residency

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
        data = {
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
            data,
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
        data = {
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
            data,
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

    def test_general_user_get_403_on_post(self):
        """Test that a general user gets a 403 response.

        I.e., the user should not be associated with any residents and
        so should not be authorized to submit the form.
        """
        # log in general user
        self.client.force_login(self.general_user)

        data = {
            "residents": [self.resident1.id],
            "activity_type": ResidentActivity.ActivityTypeChoices.OUTDOOR,
            "activity_date": date.today(),
            "activity_minutes": 30,
            "caregiver_role": ResidentActivity.CaregiverRoleChoices.NURSE,
        }

        # Make POST request
        response = self.client.post(
            self.url,
            data,
        )

        # The response should indicate a failure to process the form
        self.assertEqual(
            response.status_code,
            HTTPStatus.FORBIDDEN,
        )


class ResidentDataPreparationTest(TestCase):
    def setUp(self):
        # Create test homes
        self.home1 = HomeFactory(
            name="Home A",
        )
        self.home2 = HomeFactory(
            name="Home B",
        )

        # Create test residents
        self.resident1 = ResidentFactory()
        self.resident2 = ResidentFactory()
        self.resident3 = ResidentFactory()

        # Create residencies
        ResidencyFactory(
            home=self.home1,
            resident=self.resident1,
        )
        ResidencyFactory(
            home=self.home1,
            resident=self.resident2,
        )
        ResidencyFactory(
            home=self.home2,
            resident=self.resident3,
        )

    def test_group_residents_by_home(self):
        residencies = Residency.objects.select_related("home", "resident").all()
        grouped = group_residents_by_home(residencies)

        self.assertIn(
            self.home1.name,
            grouped,
        )
        self.assertIn(
            self.home2.name,
            grouped,
        )
        self.assertIn(
            (self.resident1.id, self.resident1.full_name),
            grouped[self.home1.name],
        )
        self.assertIn(
            (self.resident2.id, self.resident2.full_name),
            grouped[self.home1.name],
        )
        self.assertIn(
            (self.resident3.id, self.resident3.full_name),
            grouped[self.home2.name],
        )

    def test_prepare_resident_choices(self):
        residencies = Residency.objects.select_related("home", "resident").all()
        choices = prepare_resident_choices(residencies)

        # Assuming homes are sorted alphabetically in the choices list
        self.assertEqual(choices[0][0], "Home A")
        self.assertEqual(choices[1][0], "Home B")
