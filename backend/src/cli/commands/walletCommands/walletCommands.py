import logging
from typing import Annotated, Optional

import typer
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Prompt
from rich.table import Table
from src.api import fetch_info_data
from src.cli.commands.validation import validate_and_prompt_profile_name
from src.exceptions import DataFetchError
from src.services.entities import Profile
from src.utils.registry import profile_registry

from src.cli.commands.walletCommands.walletUtils import create_wallet_table

console = Console()

logger = logging.getLogger("oracle.app")


def view_wallet_command(
        profile_name: Annotated[str, typer.Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to view.")] = None
):
    profile: int = validate_and_prompt_profile_name(profile_name)
    profile: Profile = profile_registry.get(profile)

    wallet: dict[str, float] = profile.wallet
    paper_wallet: dict[str, float] = profile.paper_wallet
    wallet_table: Table = create_wallet_table(wallet=wallet, title="Wallet")
    paper_wallet_table: Table = create_wallet_table(wallet=paper_wallet, title="Paper Wallet")

    console.print(Columns([wallet_table, paper_wallet_table]))


def update_wallet_command(
        profile_name: Annotated[
            str, typer.Argument(help="The [bold]name[/bold] of the [bold]profile[/bold] to view.")] = None,
        added_tickers: Annotated[
            list[str], typer.Option("--add-ticker", "-at", help="List of [bold]tickers[/bold] to be added. Must be UPPERCASE")] = [],
        removed_tickers: Annotated[
            list[str], typer.Option("--remove-ticker", "-rt", help="List of [bold]tickers[/bold] to be removed.")] = [],
        prompt: Annotated[bool, typer.Option("--no-prompt", "-np", help="Prompt for ticker input.")] = True
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile: Profile = profile_registry.get(profile_id)

    started_wallet: dict[str, float] = profile.wallet
    final_wallet: dict[str, float] = started_wallet.copy()
    invalid_added_tickers: list[str] = []
    invalid_removed_tickers: list[str] = []
    dublicate_tickers: list[str] = []

    def add_to_wallet(ticker: str) -> bool:
        nonlocal final_wallet
        if ticker not in final_wallet:
            final_wallet[ticker] = 0
            return True
        return False

    def remove_from_wallet(ticker: str) -> bool:
        nonlocal final_wallet
        if ticker in final_wallet:
            del final_wallet[ticker]
            return True
        return False

    # Handle added tickers
    total_tickers: int = len(added_tickers) + len(removed_tickers)
    i = 1
    if added_tickers:
        with Progress() as progress:
            task = progress.add_task("Updating wallet...", total=total_tickers)

            for ticker in removed_tickers:
                progress.update(task, advance=1, description=f"Removing ticker {ticker}... {i}/{total_tickers}")
                i += 1

                if ticker != ticker.upper():
                    console.print(f"[bold red]Ticker must be in uppercase![/bold red]")
                    continue

                if not remove_from_wallet(ticker):
                    invalid_removed_tickers.append(ticker)


            for ticker in added_tickers:
                progress.update(task, advance=1, description=f"Adding ticker {ticker}... {i}/{total_tickers}")
                i += 1

                try:
                    fetch_info_data(ticker)
                    if not add_to_wallet(ticker):
                        dublicate_tickers.append(ticker)
                except DataFetchError as e:
                    invalid_added_tickers.append(ticker)
                    continue


            progress.update(task, completed=total_tickers, description="[bold green]Wallet updated![/bold green]")


    # Handle output for invalid tickers
    for invalid_ticker in invalid_added_tickers:
        console.print(f"[bold red]Invalid ticker: '{invalid_ticker}' hasn't been added to wallet[/bold red].")

    for dublicate_ticker in dublicate_tickers:
        console.print(f"[bold yellow]Ticker [bold]{dublicate_ticker}[/bold] already exists in wallet.")

    for invalid_ticker in invalid_removed_tickers:
        console.print(
            f"[bold red]Ticker '{invalid_ticker}' doesn't exist in wallet! [/bold red].")


    if prompt:
        console.print(create_wallet_table(wallet=final_wallet, title="Wallet"))

        console.print(Panel("[bold yellow]Enter the ticker for each asset you want to [white underline]`track`[/white underline].\n"
                        "To exit, press [white underline]`enter`[/white underline].", expand=False))

    # Prompt for adding and removing tickers interactively
    while prompt:
        # Use rich prompt for better user interaction
        ticker_prompt = Prompt.ask("[bold green]Enter ticker[/bold green]")

        if ticker_prompt.lower() == "":
            break

        elif ticker_prompt == "":
            console.print("[bold red]Ticker cannot be empty.[/bold red]")
            continue
        elif ticker_prompt != ticker_prompt.upper():
            console.print("[bold red]Ticker must be in uppercase![/bold red]")
            continue

        # TODO: VALIDATE TICKER
        if add_to_wallet(ticker_prompt):
            console.print(
                f"[bold green]Ticker '[bold]{ticker_prompt}[/bold]' added successfully to wallet![/bold green]")
        else:
            console.print(
                f"[bold yellow]Ticker [bold]{ticker_prompt}[/bold] already exists in wallet.[/bold yellow]")

    if prompt:
        console.print(Panel("[bold yellow]Enter the ticker for each asset you want to [white underline]`remove`[/white underline].\n"
                            "To exit, type [white underline]`enter`[/white underline].", expand=False))

    while prompt:
        ticker_prompt = Prompt.ask("[bold red]Enter ticker[/bold red]")

        if ticker_prompt.lower() == "":
            break

        if ticker_prompt == "":
            console.print("[bold red]Ticker cannot be empty.[/bold red]")
            continue

        try:
            if remove_from_wallet(ticker_prompt):
                console.print(
                    f"[bold green]Ticker '[bold]{ticker_prompt}[/bold]' removed successfully from wallet![/bold green]")
            else:
                console.print(
                    f"[bold red]Ticker '{ticker_prompt}' doesn't exist in wallet![/bold red].")
        except DataFetchError as e:
            console.print(f"[bold red]Invalid ticker: [bold]{ticker_prompt}[/bold red]. Please try again.")
            continue

    final_wallet_table = create_wallet_table(final_wallet, "Final Wallet", transient=False, print_info=True)

    removed: set = set(started_wallet.keys()) - set(final_wallet.keys())
    added: set = set(final_wallet.keys()) - set(started_wallet.keys())

    # Present changes in a table format
    changes_table = Table(title="Changes to Wallet", box=box.ROUNDED, show_header=True)
    changes_table.add_column("Ticker", justify="center", style="bold cyan")
    changes_table.add_column("Action", justify="center", style="bold")

    for ticker in added:
        changes_table.add_row(ticker, "[bold green]Added[/bold green]")

    for ticker in removed:
        changes_table.add_row(ticker, "[bold red]Removed[/bold red]")

    console.print(
        Panel(Columns([create_wallet_table(started_wallet, title="Wallet", transient=False, print_info=False), changes_table, final_wallet_table]),
              title="Wallet Changes", border_style="bold magenta", expand=False))

    # Beautiful validation prompt with changes listed
    validation_prompt = Prompt.ask(f"[bold green]Do you want to update the profile Wallet?[/bold green]",
                                   choices=["y", "n"], default="y")

    if validation_prompt != "y":
        typer.Abort()
        return

    pw_final_wallet: dict[str, float] = {}
    for ticker in final_wallet.keys():
        pw_wallet: dict[str, float] = profile.paper_wallet
        if ticker in pw_wallet.keys():
            pw_final_wallet[ticker] = pw_wallet[ticker]
        else:
            pw_final_wallet[ticker] = 0

    if profile.update(wallet=final_wallet, paper_wallet=pw_final_wallet):
        console.print(f"[bold green]Profile '[bold]{profile_name}; ID: {profile.id}[/bold]' wallet successfully updated![/bold green]")
    else:
        console.print(f"[bold]Error:[/bold] Unable to update profile '[bold]{profile_name}; ID: {profile.id}[/bold]'.\n"
                      f"Use the [underline bold green]'list-profiles'[/underline bold green] command to view available profiles.\n",
                      f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
                      style="red")


def clear_wallet_command(
        profile_name: Annotated[
            Optional[str], typer.Argument(help="The [bold]name[/bold] of the [bold]profile[/bold] to clear.")] = None,
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile: Profile = profile_registry.get(profile_id)

    wallet = profile.wallet

    i: int = 1
    for ticker, quantity in wallet.items():
        i += 1

        if quantity != 0:
            console.print(
                f"[bold red]Error:[/bold] Unable to clear wallet for profile '[bold]{profile_name}[/bold]'.\n"
                f"Wallet contains of {ticker} '[bold]{quantity}[/bold]. Please sell all assets before clearing the wallet.[/bold red]",
                style="red")
            typer.Abort()

    console.print(create_wallet_table(wallet, title="Wallet"))

    conformation: str = Prompt.ask("[bold red]Are you sure you want to clear the wallet?[/bold red]",
                                   choices=["y", "n"], default="n")

    if conformation == "y":
        if profile.update(wallet={}, paper_wallet={}):
            console.print(
                f"[bold green]Profile '[bold]{profile_name}[/bold]' wallet successfully cleared![/bold green]")
        else:
            console.print(
                f"[bold]Error:[/bold] Unable to clear profile '[bold]{profile_name}[/bold]'. Check the [underline bold green]'logs'[/underline bold green] for more details.",
                style="red")
