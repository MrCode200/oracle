from typing import Annotated

from rich.console import Console
from rich.prompt import Confirm
from rich.text import Text

from src.database import ProfileDTO
from src.cli.commands.profileCommands.utils import validate_and_prompt_profile_name
from src.database import create_profile, delete_profile
from typer import Option, Argument
from src.services.entities import Profile
from src.utils.registry import profile_registry

console = Console()

def command_create_profile(
        profile_name: str = Option(None, "--name", "-n", help="The name of the profile to create.", prompt=True),
        balance: float = Option(0, "--balance", "-b", help="The balance of the profile.", prompt="Enter balance "),
        paper_balance: float = Option(0, "--paper-balance", "-p", help="The paper balance of the profile.",
                                      prompt="Enter paper balance ")):
    new_profile: ProfileDTO = create_profile(
        name=profile_name,
        balance=balance,
        wallet={},
        paper_balance=paper_balance,
        strategy_settings={},
    )

    _ = Profile(new_profile)


def command_delete_profile(
        profile_name: Annotated[str, Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to delete.")] = None,

):
    profile_name = validate_and_prompt_profile_name(profile_name)
    if profile_name is None:
        return

    confirmation_prompt = Text(
        f"[yellow]Are you sure you want to delete the profile [bold]'{profile_name}'[/bold]? This action is irreversible.[/yellow]",
    )
    confirmation = Confirm.ask(str(confirmation_prompt), choices=["y", "n"], default="n")

    if confirmation is False:
        console.print("[bold green]Operation cancelled.[/bold green]")
        return

    # if profile_registry.get(profile_name).deactivate():
    if delete_profile(name=profile_name):
        console.print(f"[bold green]Profile '[bold]{profile_name}[/bold]' successfully deleted![/bold green]")
    else:
        console.print(
            f"[bold]Error:[/bold] Unable to delete profile '[bold]{profile_name}[/bold]'.\n"
            f"Use the [underline bold green]'list-profiles'[/underline bold green] command to view available profiles.\n",
            f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
            style="red",
        )
