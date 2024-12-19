from typing import Annotated, Optional

from rich.console import Console
from rich.prompt import Confirm
from rich.text import Text
from src.cli.commands.utils import validate_and_prompt_profile_name
from src.database import ProfileDTO, create_profile, delete_profile, update_profile
from src.services.entities import Profile
from typer import Argument, Option

console = Console()


def create_profile_command(
        profile_name: Annotated[str, Argument(help="The name of the profile to create.")],
        balance: Annotated[float, Option("--balance", "-b", help="The balance of the profile.",
                                        prompt="Enter balance", min=0.0)] = 0.0,
        paper_balance: Annotated[float, Option("--paper-balance", "-p", help="The paper balance of the profile.",
                                               prompt="Enter paper balance", min=0.0)] = 0.0,
        buy_limit: Annotated[float, Option("--buy-limit", "-bl", help="The buy limit of the profile.",
                                           prompt="Enter buy limit", min=0.0, max=1.0)] = 0.8,
        sell_limit: Annotated[float, Option("--sell-limit", "-sl", help="The sell limit of the profile.",
                                            prompt="Enter sell limit", min=-1.0, max=0.0)] = -0.8,
):
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



# TODO: Update profile command
def update_profile_command(
        new_profile_name: Annotated[Optional[str], Option("--new-name", "-n", help="The new name of the profile.")],
        balance: Annotated[Optional[float], Option(None, "--balance", "-b", help="The balance of the profile.", min=0)],
        paper_balance: Annotated[Optional[float], Option(None, "--paper-balance", "-p", help="The paper balance of the profile.", min=0)],
        buy_limit: Annotated[
            Optional[float], Option(None, "--buy-limit", "-bl", help="The buy limit of the profile.", min=0, max=1)],
        sell_limit: Annotated[Optional[float], Option(None, "--sell-limit", "-sl", help="The sell limit of the profile.",
                                            prompt="Enter sell limit ", min=-1, max=0)],

        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to update.")] = None,
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)

    if update_profile(id=profile_id, name=new_profile_name, balance=balance, paper_balance=paper_balance, buy_limit=buy_limit, sell_limit=sell_limit):
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
