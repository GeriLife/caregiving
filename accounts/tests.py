from django.test import TestCase
from django.contrib.auth import get_user_model

from residents.factories import ResidentFactory, ResidencyFactory
from homes.factories import HomeFactory, HomeUserRelationFactory


User = get_user_model()


class CanManageResidentsTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="superuser",
            email="superuser@test.com",
            password="testpassword",
        )
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@test.com",
            password="testpassword",
        )

        self.home1 = HomeFactory()
        self.home2 = HomeFactory()

        self.resident1 = ResidentFactory()
        self.resident2 = ResidentFactory()

        ResidencyFactory(
            resident=self.resident1,
            home=self.home1,
        )
        ResidencyFactory(
            resident=self.resident2,
            home=self.home2,
        )

        HomeUserRelationFactory(
            home=self.home1,
            user=self.regular_user,
        )

    def test_superuser_can_manage_all_residents(self):
        resident_ids = [self.resident1.id, self.resident2.id]
        self.assertTrue(self.superuser.can_manage_residents(resident_ids))

    def test_regular_user_can_manage_associated_residents(self):
        resident_ids = [
            self.resident1.id,
        ]
        self.assertTrue(self.regular_user.can_manage_residents(resident_ids))

    def test_regular_user_cannot_manage_unassociated_residents(self):
        resident_ids = [
            self.resident2.id,
        ]
        self.assertFalse(self.regular_user.can_manage_residents(resident_ids))
