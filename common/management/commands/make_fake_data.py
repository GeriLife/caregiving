from django.core.management.base import BaseCommand
from django.db import transaction
import datetime
import random

from homes.factories import HomeFactory
from metrics.models import ResidentActivity
from residents.factories import ResidentFactory, ResidencyFactory

NUM_HOMES = 5
NUM_RESIDENTS_PER_HOME = range(5, 10)
NUM_ACTIVITIES_PER_RESIDENT = range(10, 120)
ACTIVITY_DAYS_AGO = range(0, 90)
ACTIVITY_MINUTES = range(30, 120)


class Command(BaseCommand):
    help = "Creates fake homes, residents, residencies, and resident activities."

    def handle(self, *args, **options):
        with transaction.atomic():
            homes = HomeFactory.create_batch(NUM_HOMES)
            today = datetime.date.today()

            for home in homes:
                num_residents = random.choice(NUM_RESIDENTS_PER_HOME)
                residents = ResidentFactory.create_batch(num_residents)

                residencies = [
                    ResidencyFactory.create(
                        resident=resident,
                        home=home,
                    )
                    for resident in residents
                ]

                # Prepare and bulk create activities for all residents in this home
                all_activities = []
                for residency in residencies:
                    num_activities = random.choice(NUM_ACTIVITIES_PER_RESIDENT)
                    activities = [
                        ResidentActivity(
                            resident=residency.resident,
                            activity_date=today
                            - datetime.timedelta(days=random.choice(ACTIVITY_DAYS_AGO)),
                            home=home,
                            residency=residency,  # Associate Residency with ResidentActivity
                            activity_type=random.choice(
                                ResidentActivity.ActivityTypeChoices.choices,
                            )[0],
                            activity_minutes=random.choice(ACTIVITY_MINUTES),
                            caregiver_role=random.choice(
                                ResidentActivity.CaregiverRoleChoices.choices,
                            )[0],
                        )
                        for _ in range(num_activities)
                    ]
                    all_activities.extend(activities)

                ResidentActivity.objects.bulk_create(all_activities)

        self.stdout.write(self.style.SUCCESS("Successfully created fake data"))
