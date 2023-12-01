from django.core.management.base import BaseCommand
from homes.factories import HomeFactory


class Command(BaseCommand):
    help = "Creates fake homes."

    def add_arguments(self, parser):
        parser.add_argument("num", type=int, help="Number of homes to create")

    def handle(self, *args, **options):
        # Resident Number Verification
        if options["num"] >= 0:
            for _ in range(options["num"]):
                HomeFactory.create()
            self.stdout.write(f"Created {options['num']} fake homes.")
            return

        self.stdout.write("Invalid n. Please try again.")
