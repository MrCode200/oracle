from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from src.database import get_profile
from src.services.entities import Profile, Status
from src.utils.registry import profile_registry

from src.cli.commands.profileCommands.utils import validate_and_prompt_profile_name

console = Console()

def command_list_profiles():
    profiles = get_profile()

    if len(profiles) == 0:
        console.print("[bold red]No profiles created. Create a new Profile with the 'profile create' command.[/bold red]")
        return

    console.print("[bold green]Available profiles:[/bold green]")

    # Create a table to display profiles
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Status")

    for profile in profiles:
        status = Status(profile.status)
        table.add_row(str(profile.id), profile.name, str(status))

    console.print(table)


def command_activate_profile(
        name: Annotated[Optional[str], typer.Argument(help="The name of the profile to delete.")] = None
):
    name = validate_and_prompt_profile_name(name)

    profile: Profile = profile_registry.get(name)
    if not profile:
        console.print(f"[bold red]Error: Profile '[white underline bold]{name}[/white underline bold]' not found!\n"
                      f"The bot may not be running or the profile may have been deleted.")
        return

    if profile.activate():
        console.print(f"[bold green]Profile '[white underline bold]{name}[/white underline bold]' activated successfully!")
    else:
        console.print(f"[bold red]Error: Profile '[white underline bold]{name}[/white underline bold]' couldn't be activated!")


def command_deactivate_profile(
        name: Annotated[Optional[str], typer.Argument(help="The name of the profile to delete.")] = None
):
    name = validate_and_prompt_profile_name(name)

    profile: Profile = profile_registry.get(name)
    if not profile:
        console.print(f"[bold red]Error: Profile '[white underline bold]{name}[/white underline bold]' not found!\n"
                      f"The bot may not be running or the profile may have been deleted.")
        return

    if profile.deactivate():
        console.print(f"[bold green]Profile '[white underline bold]{name}[/white underline bold]' deactivated successfully!")
    else:
        console.print(f"[bold red]Error:Profile '[white underline bold]{name}[/white underline bold]' couldn't be deactivated!")
