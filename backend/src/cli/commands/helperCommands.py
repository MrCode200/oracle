from rich.console import Console
from rich.table import Table
from src.database import get_profile
from src.services.entities import Status
from src.utils.registry import indicator_registry

# Create a Console instance for rich output
console = Console()


def command_list_indicators():
    console.print("[bold green]Available algorithms:[/bold green]")

    # Create a table to display the indicators
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Number", style="dim")
    table.add_column("Indicator Name")

    i: int = 1
    for indicator in indicator_registry.get().keys():
        table.add_row(str(i), indicator)
        i += 1

    console.print(table)


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
