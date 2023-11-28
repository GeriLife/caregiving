from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates fake residents."

    def add_arguments(self, parser):
        parser.add_argument("num", type=int, help="Number of residents to create")
        parser.add_argument(
            "--hiatus-chance",
            type=float,
            nargs="?",
            help="Probability that a resident is on hiatus. Defaults to 0.5",
        )

    def handle(self, *args, **options):
        # Parse Arguments
        n = options["num"]
        hiatus_chance = options["hiatus_chance"]

        # Resident Number Verification
        if n < 0:
            self.stdout.write("Invalid n. Please try again.")
            return

        # Check if Hiatus Chance is Specified
        if hiatus_chance:
            # Hiatus Chance Verification
            if hiatus_chance < 0 or hiatus_chance > 1:
                self.stdout.write("Invalid hiatus chance. Please try again.")
                return

            # Create with Specified Hiatus Chance
            self.stdout.write(
                f"Created {n} fake residents with hiatus chance {hiatus_chance}.",
            )
            return

        # Create with Default Hiatus Chance
        self.stdout.write(
            f"Created {n} fake residents with default hiatus chance (0.5).",
        )
