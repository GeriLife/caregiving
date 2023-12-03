from django.core.management.base import BaseCommand
from residents.factories import ResidentFactory


class Command(BaseCommand):
    help = "Creates fake residencies. Requires residents and homes."

    def add_arguments(self, parser):
        parser.add_argument("num", type=int, help="Number of residencies to create")

    def handle(self, *args, **options):
        # Resident Number Verification
        if options["num"] >= 0:
            for _ in range(options["num"]):
                ResidentFactory.create()
            self.stdout.write(f"Created {options['num']} fake residencies.")
            return

        self.stdout.write("Invalid n. Please try again.")

    # def additional_logic(self):
    #     return True

    # def handle(self, *args, **options):
    #     # Parse Arguments
    #     n = options["num"]

    #     # Home Number Verification
    #     if n < 0 and self.additional_logic():
    #         self.stdout.write("Invalid n. Please try again.")
    #         return

    #     self.stdout.write(f"Created {n} fake residencies.")
