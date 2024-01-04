from datetime import date, timedelta
from io import StringIO
from django.core.management import call_command

from django.core.management.base import CommandError
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.constants import WEEKLY_ACTIVITY_RANGES
from metrics.factories import ResidentActivityFactory
from metrics.models import ResidentActivity
from residents.models import Residency, Resident

from .factories import HomeFactory, HomeGroupFactory, HomeUserRelationFactory
from .models import Home, HomeGroup, HomeUserRelation
from residents.factories import ResidentFactory, ResidencyFactory

User = get_user_model()


class HomeModelTests(TestCase):
    def setUp(self):
        # Create test data using factories
        self.home1 = HomeFactory(name="Home 1")

        self.home_1_current_resident_inactive = ResidentFactory(first_name="Alice")
        self.home_1_current_resident_active = ResidentFactory(first_name="Barbara")
        self.home_1_current_resident_low_active = ResidentFactory(first_name="Paulene")

        self.home_1_past_resident = ResidentFactory(first_name="Bob")

        ResidencyFactory(
            resident=self.home_1_current_resident_inactive,
            home=self.home1,
            move_in="2020-01-01",
            move_out=None,
        )
        self.home_1_current_resident_low_active_residency = ResidencyFactory(
            resident=self.home_1_current_resident_low_active,
            home=self.home1,
            move_in="2020-01-01",
            move_out=None,
        )
        self.home_1_current_resident_active_residency = ResidencyFactory(
            resident=self.home_1_current_resident_active,
            home=self.home1,
            move_in="2020-01-01",
            move_out=None,
        )
        ResidencyFactory(
            resident=self.home_1_past_resident,
            home=self.home1,
            move_in="2020-01-02",
            move_out="2020-02-01",
        )

        today = timezone.now()

        self.home_1_current_resident_active_resident_activity = ResidentActivityFactory(
            resident=self.home_1_current_resident_low_active,
            activity_date=today,
            home=self.home1,
            residency=self.home_1_current_resident_low_active_residency,
        )

        for _ in range(WEEKLY_ACTIVITY_RANGES["good"]["max_inclusive"]):
            ResidentActivityFactory(
                resident=self.home_1_current_resident_active,
                activity_date=today,
                home=self.home1,
                residency=self.home_1_current_resident_active_residency,
            )

    def test_mock_data(self):
        self.assertEqual(Home.objects.count(), 1)
        self.assertEqual(Residency.objects.count(), 4)
        self.assertEqual(Resident.objects.count(), 4)
        self.assertEqual(ResidentActivity.objects.count(), 10)

        # assert home_1_current_resident_low_active in self.home_1_current_resident_active_activity.residents
        self.assertEqual(
            self.home_1_current_resident_low_active,
            self.home_1_current_resident_active_resident_activity.resident,
        )
        # assert self.home_1_current_resident_low_active.recent_activity_count == 1
        expected_recent_activity_count = 1
        self.assertEqual(
            self.home_1_current_resident_low_active.get_recent_activity_count(),
            expected_recent_activity_count,
        )

    def test_home_current_residents(self):
        current_residents_home1 = self.home1.current_residents

        expected_current_residents_count = 3
        self.assertEqual(
            current_residents_home1.count(),
            expected_current_residents_count,
        )
        self.assertIn(
            self.home_1_current_resident_inactive,
            current_residents_home1,
        )
        self.assertIn(
            self.home_1_current_resident_low_active,
            current_residents_home1,
        )
        self.assertNotIn(
            self.home_1_past_resident,
            current_residents_home1,
        )

    def test_residents_with_recent_activity_counts(self):
        residents_with_recent_activity_counts = (
            self.home1.residents_with_recent_activity_counts.all()
        )

        expected_residents_with_recent_activity_counts = [
            {
                "resident": self.home_1_current_resident_inactive,
                "recent_activity_count": 0,
            },
            {
                "resident": self.home_1_current_resident_active,
                "recent_activity_count": 9,
            },
            {
                "resident": self.home_1_current_resident_low_active,
                "recent_activity_count": 1,
            },
        ]

        # get the index and item for each expected_residents_with_recent_activity_counts
        for index, actual_resident in enumerate(residents_with_recent_activity_counts):
            expected_resident = expected_residents_with_recent_activity_counts[index]
            self.assertEqual(
                actual_resident,
                expected_resident["resident"],
            )

            self.assertEqual(
                actual_resident.get_recent_activity_count(),
                expected_resident["recent_activity_count"],
            )

    def test_home_resident_counts_by_activity_level(self):
        home1_resident_counts_by_activity_level = (
            self.home1.resident_counts_by_activity_level
        )

        expected_resident_counts_by_activity_level = {
            "total_count": 3,
            "inactive_count": 1,
            "low_active_count": 1,
            "good_active_count": 1,
            "high_active_count": 0,
        }
        self.assertEqual(
            home1_resident_counts_by_activity_level,
            expected_resident_counts_by_activity_level,
        )

    def test_get_resident_percents_by_activity_level_normalized(self):
        home1_resident_percents_by_activity_level_normalized = (
            self.home1.get_resident_percents_by_activity_level_normalized()
        )

        expected_resident_percents_by_activity_level_normalized = {
            "total_count": 3,
            "inactive_count": 1,
            "low_active_count": 1,
            "good_active_count": 1,
            "high_active_count": 0,
            "inactive_percent": 34,
            "low_active_percent": 33,
            "good_active_percent": 33,
            "high_active_percent": 0.0,
        }
        self.assertEqual(
            home1_resident_percents_by_activity_level_normalized,
            expected_resident_percents_by_activity_level_normalized,
        )

    def test_home_resident_counts_by_activity_level_chart_data(self):
        home1_resident_counts_by_activity_level_chart_data = (
            self.home1.resident_counts_by_activity_level_chart_data
        )

        expected_resident_counts_by_activity_level_chart_data = [
            {
                "activity_level_label": "Inactive",
                "activity_level_class": "danger",
                "value": 34,
            },
            {
                "activity_level_label": "Low",
                "activity_level_class": "warning",
                "value": 33,
            },
            {
                "activity_level_label": "Moderate",
                "activity_level_class": "success",
                "value": 33,
            },
            {
                "activity_level_label": "High",
                "activity_level_class": "warning",
                "value": 0.0,
            },
        ]
        self.assertEqual(
            home1_resident_counts_by_activity_level_chart_data,
            expected_resident_counts_by_activity_level_chart_data,
        )

        values_sum = sum(
            [
                item["value"]
                for item in home1_resident_counts_by_activity_level_chart_data
            ],
        )

        expected_values_sum = 100.0

        self.assertEqual(values_sum, expected_values_sum)


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


class CurrentResidentsWithRecentActivityMetadataTest(TestCase):
    def setUp(self):
        # Create a Home instance
        self.home = HomeFactory.create()

        # Create a Resident instance
        self.resident = ResidentFactory.create()

        # Create a Residency instance linking Home and Resident
        ResidencyFactory.create(home=self.home, resident=self.resident)

        # Create ResidentActivity instances
        today = date.today()
        for i in range(7):
            activity_date = today - timedelta(days=i)
            ResidentActivityFactory.create(
                resident=self.resident,
                activity_date=activity_date,
            )

    def test_current_residents_with_recent_activity_metadata(self):
        # Get the data from the property
        data = self.home.current_residents_with_recent_activity_metadata

        # Assertions
        self.assertEqual(len(data["residents"]), 1)  # Should have one resident
        self.assertEqual(data["residents"][0]["resident"], self.resident)
        self.assertEqual(
            data["residents"][0]["total_activity_count"],
            7,
        )  # Assuming one activity per day

        self.assertEqual(
            data["residents"][0]["total_active_days"],
            7,
        )  # Assuming activity every day

        # Check the start and end dates
        self.assertEqual(
            data["start_date"],
            date.today() - timedelta(days=6),
        )
        self.assertEqual(
            data["end_date"],
            date.today(),
        )

        # Check for recent activity days data
        for day_data in data["residents"][0]["recent_activity_days"]:
            self.assertIn(
                day_data["date"],
                [date.today() - timedelta(days=i) for i in range(7)],
            )
            self.assertTrue(day_data["was_active"])  # Assuming activity every day


class HomeGroupListViewTest(TestCase):
    def setUp(self):
        self.url = reverse("home-list-view")

        # Setup test users
        self.user = User.objects.create_user(
            username="testuser",
            password="password",
        )
        self.superuser = User.objects.create_superuser(
            username="admin",
            password="admin",
        )

        # Setup test home groups using factories
        self.home_group_with_home = HomeGroupFactory(name="Group with home")
        self.home_group_without_homes = HomeGroupFactory(name="Group without homes")

        # Setup test homes using factories
        self.home_with_group = HomeFactory(
            name="Home 1",
            home_group=self.home_group_with_home,
        )
        self.home_without_group = HomeFactory(
            name="Home 3",
        )
        self.home_without_user = HomeFactory(
            name="Home 4",
        )

        # associate user with homes
        self.home_user_relation_1 = HomeUserRelationFactory(
            home=self.home_with_group,
            user=self.user,
        )
        self.home_user_relation_2 = HomeUserRelationFactory(
            home=self.home_without_group,
            user=self.user,
        )

    def test_mock_data(self):
        # Check the total count of Homes, HomeGroups, and HomeUserRelations
        self.assertEqual(Home.objects.count(), 3)
        self.assertEqual(HomeGroup.objects.count(), 2)
        self.assertEqual(HomeUserRelation.objects.count(), 2)

        # Assert that homes are correctly associated with their home groups
        self.assertEqual(self.home_with_group.home_group, self.home_group_with_home)
        self.assertIsNone(self.home_without_group.home_group)
        self.assertIsNone(self.home_without_user.home_group)

        # Check if the HomeGroup with no homes actually has no homes associated
        self.assertFalse(self.home_group_without_homes.homes.exists())

        # Assert user belongs to the correct number of homes
        self.assertEqual(self.user.homes.count(), 2)

        # Check if the specific homes are associated with the user
        self.assertIn(self.home_with_group, self.user.homes.all())
        self.assertIn(self.home_without_group, self.user.homes.all())
        self.assertNotIn(self.home_without_user, self.user.homes.all())

        # Assert superuser has no homes associated
        self.assertEqual(self.superuser.homes.count(), 0)

        def test_context_data_for_regular_user(self):
            # Log in as the regular user
            self.client.login(
                username="testuser",
                password="password",
            )

            # Get the response from the HomeGroupListView
            response = self.client.get(self.url)

            # Check that the response status code is 200
            self.assertEqual(response.status_code, 200)

            # Extract the context data
            context = response.context

            # Check that homes without a group are correctly in the context
            homes_without_group = context["homes_without_group"]
            self.assertIn(self.home_without_group, homes_without_group)
            self.assertNotIn(self.home_without_user, homes_without_group)

            # Check that homes with a group are correctly in the context
            homes_with_group = context["homes_with_group"]
            self.assertIn(self.home_with_group, homes_with_group)
            self.assertNotIn(self.home_without_user, homes_with_group)

            # Ensure that the home_groups_with_homes context is correctly formatted
            home_groups_with_homes = context["home_groups_with_homes"]
            self.assertTrue(
                any(
                    group["group_name"] == self.home_group_with_home.name
                    for group in home_groups_with_homes
                ),
            )
            self.assertTrue(
                all(
                    self.home_with_group in group["homes"]
                    for group in home_groups_with_homes
                    if group["group_name"] == self.home_group_with_home.name
                ),
            )

    def test_context_data_for_superuser(self):
        # Log in as the superuser
        self.client.login(username="admin", password="admin")

        # Get the response from the HomeGroupListView
        response = self.client.get(self.url)

        # Check that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Extract the context data
        context = response.context

        # Check that all homes are in the context data, regardless of home group
        all_homes = Home.objects.all()
        homes_without_group = context["homes_without_group"]
        homes_with_group = context["homes_with_group"]

        for home in all_homes:
            if home.home_group is None:
                self.assertIn(home, homes_without_group)
            else:
                self.assertIn(home, homes_with_group)

        # Ensure that the home_groups_with_homes context is correctly formatted
        home_groups_with_homes = context["home_groups_with_homes"]
        self.assertTrue(
            any(
                group["group_name"] == self.home_group_with_home.name
                for group in home_groups_with_homes
            ),
        )
        self.assertFalse(
            any(
                group["group_name"] == self.home_group_without_homes.name
                for group in home_groups_with_homes
            ),
        )

        # Check that the homes in the context are correctly associated with the home groups
        # Find the group corresponding to home_group_with_home
        group_with_home = next(
            (
                group
                for group in home_groups_with_homes
                if group["group_name"] == self.home_group_with_home.name
            ),
            None,
        )

        # Assert that the group is found
        self.assertIsNotNone(
            group_with_home,
            "The expected home group was not found in the context.",
        )

        # Assert that home_with_group is in the found group
        self.assertIn(
            self.home_with_group,
            group_with_home["homes"],
            "Home with group was not found in the expected group.",
        )

        # home group without homes should not be in the context
        self.assertFalse(
            any(
                group["group_name"] == self.home_group_without_homes.name
                for group in home_groups_with_homes
            ),
        )

        # homes without groups should correctly list the homes
        self.assertIn(
            self.home_without_group,
            homes_without_group,
        )

    def test_home_group_list_view_uses_correct_template(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "homes/home_group_list.html")
