from django.core.management.base import BaseCommand
from residents.factories import ResidentFactory


class Command(BaseCommand):
    help = "Creates fake residents."

    def add_arguments(self, parser):
        parser.add_argument("num", type=int, help="Number of residents to create")

    def handle(self, *args, **options):
        # Resident Number Verification
        if options["num"] >= 0:
            for _ in range(options["num"]):
                ResidentFactory.create()
            self.stdout.write(f"Created {options['num']} fake residents.")
            return

        self.stdout.write("Invalid n. Please try again.")
