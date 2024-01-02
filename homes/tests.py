from datetime import date, timedelta
from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from django.core.management.base import CommandError
from django.utils import timezone

from metrics.factories import ResidentActivityFactory
from metrics.models import ResidentActivity
from residents.models import Residency, Resident

from .factories import HomeFactory
from .models import Home
from residents.factories import ResidentFactory, ResidencyFactory


class HomeModelTests(TestCase):
    def setUp(self):
        # Create test data using factories
        self.home1 = HomeFactory(name="Home 1")

        self.home_1_current_resident_inactive = ResidentFactory(first_name="Alice")
        self.home_1_current_resident_active = ResidentFactory(first_name="Paulene")

        self.home_1_past_resident = ResidentFactory(first_name="Bob")

        ResidencyFactory(
            resident=self.home_1_current_resident_inactive,
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
            resident=self.home_1_current_resident_active,
            activity_date=today,
            home=self.home1,
            residency=self.home_1_current_resident_active_residency,
        )

    def test_mock_data(self):
        self.assertEqual(Home.objects.count(), 1)
        self.assertEqual(Residency.objects.count(), 3)
        self.assertEqual(Resident.objects.count(), 3)
        self.assertEqual(ResidentActivity.objects.count(), 1)

        # assert home_1_current_resident_active in self.home_1_current_resident_active_activity.residents
        self.assertEqual(
            self.home_1_current_resident_active,
            self.home_1_current_resident_active_resident_activity.resident,
        )
        # assert self.home_1_current_resident_active.recent_activity_count == 1
        expected_recent_activity_count = 1
        self.assertEqual(
            self.home_1_current_resident_active.get_recent_activity_count(),
            expected_recent_activity_count,
        )

    def test_home_current_residents(self):
        current_residents_home1 = self.home1.current_residents

        expected_current_residents_count = 2
        self.assertEqual(
            current_residents_home1.count(),
            expected_current_residents_count,
        )
        self.assertIn(
            self.home_1_current_resident_inactive,
            current_residents_home1,
        )
        self.assertIn(
            self.home_1_current_resident_active,
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
            "total_count": 2,
            "inactive_count": 1,
            "low_active_count": 1,
            "good_active_count": 0,
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
            "total_count": 2,
            "inactive_count": 1,
            "low_active_count": 1,
            "good_active_count": 0,
            "high_active_count": 0,
            "inactive_percent": 50.0,
            "low_active_percent": 50.0,
            "good_active_percent": 0.0,
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
                "value": 50.0,
            },
            {
                "activity_level_label": "Low",
                "activity_level_class": "warning",
                "value": 50.0,
            },
            {
                "activity_level_label": "Moderate",
                "activity_level_class": "success",
                "value": 0.0,
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
