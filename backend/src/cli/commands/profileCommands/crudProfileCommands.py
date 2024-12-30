from typing import Annotated, Optional

from rich.box import ROUNDED
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text
from src.cli.commands.validation import validate_and_prompt_profile_name
from src.database import ProfileDTO, create_profile, delete_profile, update_profile
from src.services.entities import Profile
from typer import Argument, Option, Abort

from src.utils.registry import profile_registry
from src.cli.commands.profileCommands.profileUtils import isfloat

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
    invalid_profile_names = [profile.name for profile in profile_registry.get().values()]
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
        new_profile_name: Annotated[
            Optional[str], Option("--name", "-n", help="The name of the profile to create.")] = None,
        balance: Annotated[
            Optional[float], Option("--balance", "-b", help="The balance of the profile.", min=0.0)] = None,
        paper_balance: Annotated[
            Optional[float], Option("--paper-balance", "-p", help="The paper balance of the profile.", min=0.0)] = None,
        buy_limit: Annotated[
            Optional[float], Option("--buy-limit", "-bl", help="The buy limit of the profile.", min=0.0,
                                    max=1.0)] = None,
        sell_limit: Annotated[
            Optional[float], Option("--sell-limit", "-sl", help="The sell limit of the profile.", min=-1.0,
                                    max=0.0)] = None,

):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile: Profile = profile_registry.get(profile_id)

    balance = "" if balance is None else str(balance)
    paper_balance = "" if paper_balance is None else str(paper_balance)
    buy_limit = "" if buy_limit is None else str(buy_limit)
    sell_limit = "" if sell_limit is None else str(sell_limit)

    if new_profile_name is None:
        new_profile_name = Prompt.ask("[bold magenta]Enter new profile name", default=profile.name)

    while True:
        if isfloat(balance):
            balance = float(balance)

            if balance < 0:
                console.print("[bold red]Error:[/bold red] Balance must be greater than or equal to 0.",)
                balance = ""
                continue

            break

        balance = Prompt.ask("[bold magenta]Enter new balance [dim](balance >= 0)", default=str(profile.balance))

    while True:
        if isfloat(paper_balance):
            paper_balance = float(paper_balance)

            if paper_balance < 0:
                console.print("[bold red]Error:[/bold red] Paper balance must be greater than or equal to 0.",)
                paper_balance = ""
                continue

            break

        paper_balance = Prompt.ask("[bold magenta]Enter new paper balance [dim](paper_balance >= 0)", default=str(profile.paper_balance))

    while True:
        if isfloat(buy_limit):
            buy_limit = float(buy_limit)

            if buy_limit < 0 or buy_limit > 1:
                console.print("[bold red]Error:[/bold red] Buy limit must be between 0 and 1.",)
                buy_limit = ""
                continue

            break

        buy_limit = Prompt.ask("[bold magenta]Enter new buy limit [dim](0 <= buy_limit <= 1)", default=str(profile.buy_limit))

    while True:
        if isfloat(sell_limit):
            sell_limit = float(sell_limit)

            if sell_limit < -1 or sell_limit > 0:
                console.print("[bold red]Error:[/bold red] Sell limit must be between -1 and 0.",)
                sell_limit = ""
                continue

            break

        sell_limit = Prompt.ask("[bold magenta]Enter new sell limit [dim](-1 <= sell_limit <= 0)", default=str(profile.sell_limit))

    changes_table = Table(title="Changes to Profile", box=ROUNDED, show_header=True)
    changes_table.add_column("Property", justify="center", style="bold cyan")
    changes_table.add_column("Old Value", justify="center", style="bold cyan")
    changes_table.add_column("New Value", justify="center", style="bold cyan")

    if new_profile_name != profile.name:
        changes_table.add_row("Name", profile.name, new_profile_name)
    else:
        new_profile_name = profile.name

    if balance != profile.balance:
        changes_table.add_row("Balance", str(profile.balance), str(balance))

    if paper_balance != profile.paper_balance:
        changes_table.add_row("Paper Balance", str(profile.paper_balance), str(paper_balance))

    if buy_limit != profile.buy_limit:
        changes_table.add_row("Buy Limit", str(profile.buy_limit), str(buy_limit))

    if sell_limit != profile.sell_limit:
        changes_table.add_row("Sell Limit", str(profile.sell_limit), str(sell_limit))

    console.print(changes_table)

    confirmation_prompt = Text("Are you sure you want to update this profile? (y/n) ")
    confirmation = Prompt.ask(confirmation_prompt, default="y", choices=["y", "n"])
    if confirmation == "n":
        console.print("Profile update cancelled.")
        return

    if profile.update_profile(
            name=new_profile_name,
            balance=float(balance),
            paper_balance=float(paper_balance),
            buy_limit=float(buy_limit),
            sell_limit=float(sell_limit),
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
