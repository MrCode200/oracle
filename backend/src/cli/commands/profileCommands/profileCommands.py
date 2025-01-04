from typing import Annotated, Optional, Type

import typer
from rich.console import Console
from rich.table import Table
from src.cli.commands.validation import validate_and_prompt_profile_name, validate_and_prompt_status
from src.database import get_profile
from src.services.entities import Profile
from src.constants import Status
from src.utils.registry import profile_registry

console = Console()


def list_profiles_command():
    profiles = get_profile()

    if len(profiles) == 0:
        console.print(
            "[bold red]No profiles created. Create a new profile with the 'profile create' command.[/bold red]"
        )
        return

    console.print("[bold green]Available profiles:[/bold green]", style="bold underline")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold magenta")
    table.add_column("Status")
    table.add_column("Balance", style="bold green")
    table.add_column("Paper Balance", style="bold green")
    table.add_column("Buy Limit", style="bold cyan")
    table.add_column("Sell Limit", style="bold red")

    for profile in profiles:
        status = Status(profile.status)
        status_color = {
            Status.INACTIVE: "dim white",
            Status.ACTIVE: "bold green",
            Status.PAPER_TRADING: "bold bright_yellow",
            Status.GRADIANT_EXIT: "bold bright_blue",
            Status.UNKNOWN_ERROR: "bold red blink"
        }.get(status, "bold white")

        table.add_row(
            str(profile.id),
            profile.name,
            f"[{status_color}]{str(status)}",  # Use the colored status text
            f"{profile.balance}",
            f"{profile.paper_balance}",
            f"{profile.buy_limit}",
            f"{profile.sell_limit}",
        )

    console.print(table)


def change_status_command(
        profile_name: Annotated[Optional[str], typer.Argument(help="The name of the profile to delete.")] = None,
        status: Annotated[Optional[str], typer.Argument(help="The status to set the profile to. Has Autocompletes Option when not provided.")] = None,
        run_on_start: Annotated[bool, typer.Option("--run-on-start", "-r", help="Run the strategy on start")] = False
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    status: Type[Status] = validate_and_prompt_status(status)

    profile: Profile = profile_registry.get(profile_id)
    if not profile:
        console.print(f"[bold red]Error: Profile '[white underline bold]{profile_name}; ID {profile_id}[/white underline bold]' not found!\n"
                      f"The bot may not be running or the profile may have been deleted.")
        return

    if not profile_registry.get(profile_id).change_status(status=status, run_on_start=run_on_start):
        console.print(
            f"[bold red]Error: Profile '[white underline bold]{profile_name}; ID {profile_id}[/white underline bold]' couldn't change status to '[white underline bold]{status}[/white underline bold]'!")
        return

    console.print(f"[bold green]Profile '[white underline bold]{profile_name}; ID {profile_id}[/white underline bold]' changed status to '[white underline bold]{status}[/white underline bold]' successfully!")
