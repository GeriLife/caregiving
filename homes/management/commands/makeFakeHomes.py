from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates fake homes."

    def add_arguments(self, parser):
        parser.add_argument("num", type=int, help="Number of homes to create")

    def handle(self, *args, **options):
        # Parse Arguments
        n = options["num"]

        # Home Number Verification
        if n < 0:
            self.stdout.write("Invalid n. Please try again.")
            return

        self.stdout.write(f"Created {n} fake homes.")
