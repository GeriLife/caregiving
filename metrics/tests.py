from django.test import TestCase
from .models import ResidentActivity
from homes.factories import HomeFactory
from residents.factories import ResidentFactory, ResidencyFactory
from datetime import datetime
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
        self.data = {
            "residents": self.resident1,
            "activity_type": "outdoor",
            "date": datetime.now(),
            "duration_minutes": 30,
            "caregiver_role": "staff",
        }
        response = self.client.post(
            reverse("activity-form-view"),
            self.data,
            content_type="application/x-www-form-urlencoded",
        )
        print(response)
