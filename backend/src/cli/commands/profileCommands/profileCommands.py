from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table
from src.cli.commands.profileCommands.utils import (
    validate_and_prompt_profile_name, validate_and_prompt_status)
from src.database import get_profile
from src.services.entities import Profile, Status
from src.utils.registry import profile_registry

console = Console()


def list_profiles_command():
    profiles = get_profile()

    if len(profiles) == 0:
        console.print(
            "[bold red]No profiles created. Create a new Profile with the 'profile create' command.[/bold red]")
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


def change_status_command(
        name: Annotated[Optional[str], typer.Argument(help="The name of the profile to delete.")] = None,
        status: Annotated[Optional[str], typer.Argument(help="The status to set the profile to. Has Autocompletes Option when not provided.")] = None,
        run_on_start: Annotated[bool, typer.Option("--run-on-start", "-r", help="Run the strategy on start")] = False
):
    name = validate_and_prompt_profile_name(name)

    status = validate_and_prompt_status(status)

    profile: Profile = profile_registry.get(name)
    if not profile:
        console.print(f"[bold red]Error: Profile '[white underline bold]{name}[/white underline bold]' not found!\n"
                      f"The bot may not be running or the profile may have been deleted.")
        return

    confirmation: bool = False
    match status:
        case Status.ACTIVE:
            confirmation: bool = profile.activate(run_on_start)
        case Status.INACTIVE:
            confirmation: bool = profile.deactivate()
        case Status.PAPER_TRADING:
            confirmation: bool = profile.activate_paper_trading(run_on_start)

    if not confirmation:
        console.print(
            f"[bold red]Error: Profile '[white underline bold]{name}[/white underline bold]' couldn't change status to '[white underline bold]{status}[/white underline bold]'!")
        return

    console.print(f"[bold green]Profile '[white underline bold]{name}[/white underline bold]' activated successfully!")
