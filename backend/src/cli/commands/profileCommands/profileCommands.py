from typing import Annotated, Optional, Type

from rich.status import Status as st
from rich.box import ROUNDED
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
        status: Annotated[Optional[str], typer.Argument(
            help="The status to set the profile to. Has Autocompletes Option when not provided.")] = None,
        run_on_start: Annotated[bool, typer.Option("--run-on-start", "-r", help="Run the strategy on start")] = False
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    status: Type[Status] = validate_and_prompt_status(status)

    profile: Profile = profile_registry.get(profile_id)
    if not profile:
        console.print(
            f"[bold red]Error: Profile '[white underline bold]{profile_name}; ID {profile_id}[/white underline bold]' not found!\n"
            f"The bot may not be running or the profile may have been deleted.")
        return

    if not profile_registry.get(profile_id).change_status(status=status, run_on_start=run_on_start):
        console.print(
            f"[bold red]Error: Profile '[white underline bold]{profile_name}; ID {profile_id}[/white underline bold]' couldn't change status to '[white underline bold]{status}[/white underline bold]'!")
        return

    console.print(
        f"[bold green]Profile '[white underline bold]{profile_name}; ID {profile_id}[/white underline bold]' changed status to '[white underline bold]{status}[/white underline bold]' successfully!")


def backtest_profile_command(
        profile_name: Annotated[Optional[str], typer.Argument(help="The name of the profile to backtest.")] = None,
        balance: Annotated[
            Optional[float], typer.Option("--balance", "-b", help="The balance to use for the backtest.",
                                          min=1, prompt="Enter balance")] = 1_000_000,
        days: Annotated[Optional[int], typer.Option("--days", "-d", help="The number of days to backtest.", min=1,
                                                    prompt="Enter past number of days to backtest")] = 7,
        partition_amount: Annotated[Optional[int], typer.Option("--partitions", "-p", min=1,
                help="The number of partitions to divide the data into for recalculating the Return on Investment (ROI).",
                prompt="Enter number of partitions")] = 1):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile: Profile = profile_registry.get(profile_id)

    if not profile:
        console.print(
            f"[bold red]Error: Profile '[white underline bold]{profile_name}; ID {profile_id}[/white underline bold]' not found!\n"
            f"The bot may not be running or the profile may have been deleted.")
        return

    with st("Backtesting...", spinner="dots") as status:
        results: Optional[list[float]] = profile.backtest(balance=balance, days=days, partition_amount=partition_amount)

        status.update("Done!")

    if not results:
        console.print(
            f"[bold red]Error: Profile '[white underline bold]{profile_name}; ID {profile_id}[/white underline bold]' couldn't backtest!")
        return

    backtest_table: Table = Table(show_header=True, header_style="bold cyan", box=ROUNDED, style="bold")
    backtest_table.add_column("Parition", style="bold magenta")
    backtest_table.add_column("Liquidity", style="bold green")
    backtest_table.add_column("Return on Investment (ROI)")

    liquidity: list[float] = []
    for i, result in enumerate(results):
        if i == 0:
            liquidity.append(balance * result)
            continue

        liquidity.append(liquidity[i-1] * result)

    partition_date_len: float = round((days / partition_amount), 3)
    print(results)
    print(liquidity)
    for i in range(len(results)):
        if results[i] < 1:
            clr: str = f"[bold red]"
        else:
            clr: str = f"[bold green]"

        backtest_table.add_row(str(partition_date_len * i + 1) + " days", clr + str(liquidity[i]), f"{clr}{results[i]:.2%}")

    console.print(backtest_table)
