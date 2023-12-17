import argparse
import subprocess
from dataclasses import dataclass
from collections.abc import Callable


@dataclass
class Command:
    alias: str
    help_text: str
    commands_list: list[str]
    callable: Callable | None = None


def update_outdated_packages() -> None:
    """Update all outdated packages."""
    result = subprocess.run(
        "pip list --outdated --format=freeze",
        shell=True,
        text=True,
        capture_output=True,
    )
    outdated_packages = result.stdout.splitlines()

    for package in outdated_packages:
        package_name = package.split("==")[0]
        subprocess.run(f"pip install --upgrade {package_name}", shell=True)


def uninstall_all_packages() -> None:
    """Uninstall all packages."""
    installed_packages = subprocess.run(
        "pip freeze",
        shell=True,
        text=True,
        capture_output=True,
    ).stdout
    packages = installed_packages.splitlines()
    for package in packages:
        package_name = package.split("==")[0]
        subprocess.run(f"pip uninstall -y {package_name}", shell=True)


COMMANDS = [
    Command(
        alias="audit-deps",
        help_text="Audit the dependencies for updates",
        commands_list=[
            "pip list --outdated",
        ],
    ),
    Command(
        alias="start-db",
        help_text="Start the database",
        commands_list=[
            "docker compose up -d wf_postgres_service",
        ],
    ),
    Command(
        alias="stop-db",
        help_text="Stop the database",
        commands_list=[
            "docker compose stop wf_postgres_service",
        ],
    ),
    Command(
        alias="install",
        help_text="Install project dependencies",
        commands_list=[
            "python -m pip install -r requirements.txt -r requirements.dev.txt",
        ],
    ),
    Command(
        alias="test",
        help_text="Run tests",
        commands_list=[
            "python manage.py test",
        ],
    ),
    Command(
        alias="update-deps",
        help_text="Update all outdated packages to their latest versions",
        commands_list=[],
        callable=update_outdated_packages,
    ),
    Command(
        alias="uninstall-all",
        help_text="Uninstall all packages installed in the virtual environment",
        commands_list=[],
        callable=uninstall_all_packages,
    ),
]


def run_command(command: Command) -> None:
    """Executes the given command.

    If the command is callable, it will be executed directly.
    If the command is a list of shell commands, each command will be executed using subprocess.run.

    Args:
        command (Command): The command to be executed.

    Returns:
        None
    """
    if command.callable:
        command.callable()
    else:
        for cmd in command.commands_list:
            subprocess.run(cmd, shell=True, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Development tasks.")
    subparsers = parser.add_subparsers(dest="command")

    for command in COMMANDS:
        subparser = subparsers.add_parser(command.alias, help=command.help_text)
        subparser.set_defaults(command_obj=command)

    args = parser.parse_args()

    if hasattr(args, "command_obj"):
        run_command(args.command_obj)
    else:
        parser.print_help()
