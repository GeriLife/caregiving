from django.core.management.base import BaseCommand
from django.db import transaction
import datetime
import random

from caregivers.factories import CaregiverRoleFactory
from homes.factories import HomeFactory
from metrics.models import ResidentActivity
from residents.factories import ResidentFactory, ResidencyFactory
from work.factories import WorkTypeFactory, WorkFactory

NUM_HOMES = 5
NUM_RESIDENTS_PER_HOME = range(5, 10)
NUM_ACTIVITIES_PER_RESIDENT = range(10, 120)
NUM_WORK_ENTRIES = range(10, 30)
ACTIVITY_DAYS_AGO = range(0, 90)
ACTIVITY_MINUTES = range(30, 120)
WORK_MINUTES = range(30, 480)

# Predefined caregiver roles
CAREGIVER_ROLES = ["Nurse", "Practical Nurse", "Staff", "Volunteer"]

# Predefined work types
WORK_TYPES = ["Medication", "Cooking", "Cleaning", "Recreation", "Hygiene", "Wellness"]


class Command(BaseCommand):
    help = "Creates fake homes, residents, residencies, resident activities, caregiver roles, and work."

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write("Creating caregiver roles...")
            caregiver_roles = []
            for role_name in CAREGIVER_ROLES:
                role = CaregiverRoleFactory(name=role_name)
                caregiver_roles.append(role)

            self.stdout.write("Creating work types...")
            work_types = []
            for work_type_name in WORK_TYPES:
                work_type = WorkTypeFactory(name=work_type_name)
                work_types.append(work_type)

            self.stdout.write("Creating homes...")
            homes = HomeFactory.create_batch(NUM_HOMES)
            today = datetime.date.today()

            for home in homes:
                num_residents = random.choice(NUM_RESIDENTS_PER_HOME)
                self.stdout.write(
                    f"Creating {num_residents} residents for {home.name}...",
                )
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

                # Create work entries for this home
                self.stdout.write(f"Creating work entries for {home.name}...")
                num_work_entries = random.choice(NUM_WORK_ENTRIES)
                for _ in range(num_work_entries):
                    WorkFactory.create(
                        home=home,
                        type=random.choice(work_types),
                        caregiver_role=random.choice(caregiver_roles),
                        date=today
                        - datetime.timedelta(days=random.choice(ACTIVITY_DAYS_AGO)),
                        duration_minutes=random.choice(WORK_MINUTES),
                    )

        self.stdout.write(self.style.SUCCESS("Successfully created fake data"))
