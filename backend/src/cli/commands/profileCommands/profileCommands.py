from typing import Annotated, Optional

import typer
from rich.console import Console
from src.services.entities import Profile
from src.utils.registry import profile_registry

from src.cli.commands.profileCommands.utils import validate_and_prompt_profile_name

console = Console()

def command_activate_profile(
        name: Annotated[Optional[str], typer.Argument(help="The name of the profile to delete.")] = None
):
    name = validate_and_prompt_profile_name(name)

    profile: Profile = profile_registry.get(name)
    if profile:
        if profile.activate():
            console.print(f"[bold green]Profile '[white underline bold]{name}[/white underline bold]' activated successfully!")
        else:
            console.print(f"[bold red]Error: Profile '[white underline bold]{name}[/white underline bold]' couldn't be activated!")
    else:
        console.print(f"[bold red]Error: Profile '[white underline bold]{name}[/white underline bold]' not found!\n"
                      f"The bot may not be running or the profile may have been deleted.")


def command_deactivate_profile(
        name: Annotated[Optional[str], typer.Argument(help="The name of the profile to delete.")] = None
):
    name = validate_and_prompt_profile_name(name)

    profile: Profile = profile_registry.get(name)
    if profile:
        if profile.deactivate():
            console.print(f"[bold green]Profile '[white underline bold]{name}[/white underline bold]' deactivated successfully!")
        else:
            console.print(f"[bold red]Error:Profile '[white underline bold]{name}[/white underline bold]' couldn't be deactivated!")
    else:
        console.print(f"[bold red]Error: Profile '[white underline bold]{name}[/white underline bold]' not found!\n"
                      f"The bot may not be running or the profile may have been deleted.")