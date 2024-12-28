from typing import Annotated, Optional

from rich.console import Console
from rich.prompt import Confirm
from rich.text import Text
from src.cli.commands.validation import validate_and_prompt_profile_name
from src.database import ProfileDTO, create_profile, delete_profile, update_profile
from src.services.entities import Profile
from typer import Argument, Option, Abort

from src.utils.registry import profile_registry

console = Console()


def create_profile_command(
        profile_name: Annotated[str, Argument(help="The name of the profile to create.")],
        balance: Annotated[float, Option("--balance", "-b", help="The balance of the profile.",
                                         prompt="Enter balance", min=0.0)] = 0.0,
        paper_balance: Annotated[float, Option("--paper-balance", "-pb", help="The paper balance of the profile.",
                                               prompt="Enter paper balance", min=0.0)] = 0.0,
        buy_limit: Annotated[float, Option("--buy-limit", "-bl", help="The buy limit of the profile.",
                                           prompt="Enter buy limit", min=0.0, max=1.0)] = 0.8,
        sell_limit: Annotated[float, Option("--sell-limit", "-sl", help="The sell limit of the profile.",
                                            prompt="Enter sell limit", min=-1.0, max=0.0)] = -0.8,
):
    invalid_profile_names = [profile.name for profile in profile_registry.get()]
    if profile_name in invalid_profile_names:
        console.print(
            f"[bold]Error:[/bold] Profile '[bold]{profile_name}[/bold]' already exists.\n"
            f"Use the [underline bold green]'profile list'[/underline bold green] command to view available profiles.",
            style="red",
        )
        return

    new_profile: ProfileDTO = create_profile(
        name=profile_name,
        balance=balance,
        wallet={},
        paper_balance=paper_balance,
        buy_limit=buy_limit,
        sell_limit=sell_limit,
    )

    _ = Profile(new_profile)

    console.print(
        f"[bold green]Profile '[white underline bold]{profile_name}[/white underline bold]' created successfully![/bold green]")


def update_profile_command(
        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to update.")] = None,
        new_profile_name: Annotated[str, Option("--name", "-n", help="The name of the profile to create.")] = None,
        balance: Annotated[float, Option("--balance", "-b", help="The balance of the profile.",
                                         prompt="Enter balance", min=0.0)] = 0.0,
        paper_balance: Annotated[float, Option("--paper-balance", "-p", help="The paper balance of the profile.",
                                               prompt="Enter paper balance", min=0.0)] = 0.0,
        buy_limit: Annotated[float, Option("--buy-limit", "-bl", help="The buy limit of the profile.",
                                           prompt="Enter buy limit", min=0.0, max=1.0)] = 0.8,
        sell_limit: Annotated[float, Option("--sell-limit", "-sl", help="The sell limit of the profile.",
                                            prompt="Enter sell limit", min=-1.0, max=0.0)] = -0.8,

):
    profile_id: int = validate_and_prompt_profile_name(profile_name)

    if profile_registry.get(profile_id).update_profile(
            name=new_profile_name,
            balance=balance,
            paper_balance=paper_balance,
            buy_limit=buy_limit,
            sell_limit=sell_limit
    ):
        console.print(f"[bold green]Profile '[bold]{profile_name}[/bold]' successfully updated![/bold green]")
    else:
        console.print(
            f"[bold]Error:[/bold] Unable to update profile '[bold]{profile_name}[/bold]'.\n"
            f"Use the [underline bold green]'list-profiles'[/underline bold green] command to view available profiles.\n",
            f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
            style="red",
        )


def delete_profile_command(
        profile_name: Annotated[str, Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to delete.")] = None,
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    if profile_id is None:
        Abort()
        return
    confirmation_prompt = Text(
        f"[yellow]Are you sure you want to delete the profile [bold]'{profile_name}'[/bold]? This action is irreversible.[/yellow]",
    )
    confirmation = Confirm.ask(str(confirmation_prompt), choices=["y", "n"], default="n")

    if confirmation is False:
        console.print("[bold green]Operation cancelled.[/bold green]")
        return

    if delete_profile(id=profile_id):
        console.print(f"[bold green]Profile '[bold]{profile_name}[/bold]' successfully deleted![/bold green]")
    else:
        console.print(
            f"[bold]Error:[/bold] Unable to delete profile '[bold]{profile_name}[/bold]'.\n"
            f"Use the [underline bold green]'list-profiles'[/underline bold green] command to view available profiles.\n",
            f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
            style="red",
        )
