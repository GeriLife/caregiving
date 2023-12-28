import datetime
import random
from django.core.management.base import BaseCommand

from homes.factories import HomeFactory
from metrics.models import ResidentActivity
from residents.factories import ResidentFactory, ResidencyFactory


NUM_HOMES = 5
NUM_RESIDENTS_PER_HOME = range(5, 10)
NUM_ACTIVITIES_PER_RESIDENT = range(0, 14)
ACTIVITY_DAYS_AGO = range(0, 8)
ACTIVITY_MINUTES = range(30, 120)


class Command(BaseCommand):
    help = "Creates fake homes, residents, residencies, and resident activities."

    def handle(self, *args, **options):
        """Creates fake homes, residents, residencies, and resident
        activities."""
        homes = HomeFactory.create_batch(NUM_HOMES)
        today = datetime.date.today()

        homes_created = len(homes)
        residents_created = 0
        residencies_created = 0
        activities_created = 0

        for home in homes:
            num_residents = random.choice(NUM_RESIDENTS_PER_HOME)
            residents = ResidentFactory.create_batch(num_residents)
            residents_created += len(residents)

            # Create residencies
            for resident in residents:
                residency = ResidencyFactory.create(
                    resident=resident,
                    home=home,
                )
                residencies_created += 1

                # Create activities
                num_activities = random.choice(NUM_ACTIVITIES_PER_RESIDENT)

                for _ in range(num_activities):
                    # date within last N days
                    activity_date = today - datetime.timedelta(
                        days=random.choice(ACTIVITY_DAYS_AGO),
                    )
                    activity_type = random.choice(
                        ResidentActivity.ActivityTypeChoices.choices,
                    )[0]
                    activity_minutes = random.choice(ACTIVITY_MINUTES)
                    caregiver_role = random.choice(
                        ResidentActivity.CaregiverRoleChoices.choices,
                    )[0]

                    ResidentActivity.objects.create(
                        resident=resident,
                        activity_date=activity_date,
                        residency=residency,
                        home=home,
                        activity_type=activity_type,
                        activity_minutes=activity_minutes,
                        caregiver_role=caregiver_role,
                        # TODO: consider adding group_activity_id
                    )
                    activities_created += 1

        self.stdout.write(f"Created {homes_created} fake homes.")
        self.stdout.write(f"Created {residents_created} fake residents.")
        self.stdout.write(f"Created {residencies_created} fake residencies.")
        self.stdout.write(f"Created {activities_created} fake activities.")
