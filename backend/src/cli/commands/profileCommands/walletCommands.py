from typing import Annotated, Optional

import typer
from rich.columns import Columns

from api import fetch_info_data
from rich import box
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.prompt import Prompt
from rich.panel import Panel

from database import update_profile, get_profile
from src.exceptions import DataFetchError

from src.cli.commands.profileCommands.utils import validate_and_prompt_profile_name

console = Console()


def get_ticker_price(ticker: str) -> float:
    info = fetch_info_data(ticker)
    current_price = info.get("currentPrice", None)

    if current_price is None:
        current_price = info.get("regularMarketPreviousClose", None)

    return current_price


def create_wallet_table(wallet: dict[str, float], title: str, transient: bool = True, print_info: bool = True) -> Table:
    final_wallet: dict[str, float] = wallet.copy()
    invalid_tickers: list[str] = []

    with Progress(transient=transient) as progress:
        final_wallet_task = progress.add_task("Fetching wallet...")

        progress.update(final_wallet_task, description="Creating wallet table...", total=len(final_wallet) + 1)
        progress.update(final_wallet_task, advance=1)

        final_wallet_table = Table(title=title, box=box.ROUNDED, show_header=True, header_style="bold magenta")
        final_wallet_table.add_column("", style="dim")
        final_wallet_table.add_column("Ticker", style="bold cyan")
        final_wallet_table.add_column("Quantity", style="bold cyan")
        final_wallet_table.add_column("Value", style="bold green")
        final_wallet_table.add_column("Holding Value", style="bold green")

        i = 1
        for ticker, quantity in wallet.items():
            progress.update(final_wallet_task, description=f"Fetching prices of {ticker}... {i}/{len(final_wallet)}",
                            advance=1)

            current_price: Optional[float] = get_ticker_price(ticker)

            if current_price is None:
                invalid_tickers.append(ticker)
            else:
                holding_value: float = current_price * quantity

                final_wallet_table.add_row(str(i), ticker, str(quantity), str(current_price) + "$",
                                           str(holding_value) + "$")
            i += 1

    for ticker in invalid_tickers:
        console.print(f"[bold yellow] {ticker} has been identified as an invalid ticker. Skipping...[/bold yellow]") if print_info else None
        wallet.pop(ticker)

    if print_info and invalid_tickers:
        console.print(f"[bold red]Update wallet to remove invalid tickers![/bold red]")

    return final_wallet_table


def command_view_wallet(
        profile_name: Annotated[str, typer.Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to view.")] = None
):
    profile_name = validate_and_prompt_profile_name(profile_name)

    table = create_wallet_table(get_profile(name=profile_name).wallet, title="Wallet")

    console.print(table)


def command_update_wallet(
        profile_name: Annotated[
            str, typer.Argument(help="The [bold]name[/bold] of the [bold]profile[/bold] to view.")] = None,
        added_tickers: Annotated[
            list[str], typer.Option("--add-ticker", "-at", help="List of [bold]tickers[/bold] to update.")] = [],
        removed_tickers: Annotated[
            list[str], typer.Option("--remove-ticker", "-rt", help="List of [bold]tickers[/bold] to update.")] = [],
        prompt: Annotated[bool, typer.Option("--no-prompt", "-np", help="Prompt for ticker input.")] = True
):
    profile_name: str = validate_and_prompt_profile_name(profile_name)

    started_wallet: dict[str, float] = get_profile(name=profile_name).wallet
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
        if ticker in final_wallet and final_wallet[ticker] == 0:
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
                progress.update(task, advance=1, description=f"Removing ticker {ticker}... {i}/{total_tickers}...")
                i += 1

                if not remove_from_wallet(ticker):
                    invalid_removed_tickers.append(ticker)


            for ticker in added_tickers:
                progress.update(task, advance=1, description=f"Adding ticker {ticker}... {i}/{total_tickers}...")
                i += 1

                try:
                    fetch_info_data(ticker)
                    if not add_to_wallet(ticker):
                        dublicate_tickers.append(ticker)
                except DataFetchError as e:
                    invalid_added_tickers.append(ticker)
                    continue


    # Handle output for invalid tickers
    for invalid_ticker in invalid_added_tickers:
        console.print(f"[bold red]Invalid ticker: '{invalid_ticker}' hasn't been added to wallet[/bold red].")

    for dublicate_ticker in dublicate_tickers:
        console.print(f"[bold yellow]Ticker [bold]{dublicate_ticker}[/bold] already exists in wallet.")

    for invalid_ticker in invalid_removed_tickers:
        console.print(
            f"[bold red]Ticker '{invalid_ticker}' doesn't exist in wallet or contains assets, \n in such a case pls sell all assets before removing [/bold red].")

    # Prompt for adding and removing tickers interactively
    while prompt:
        # Use rich prompt for better user interaction
        ticker_prompt = Prompt.ask("[bold green]Enter ticker[/bold green]")

        if ticker_prompt.lower() == "q":
            break

        if ticker_prompt == "":
            console.print("[bold red]Ticker cannot be empty.[/bold red]")
            continue

        try:
            fetch_info_data(ticker_prompt)  # Assuming it fetches the data for the ticker
            if add_to_wallet(ticker_prompt):
                console.print(
                    f"[bold green]Ticker '[bold]{ticker_prompt}[/bold]' added successfully to wallet![/bold green]")
            else:
                console.print(
                    f"[bold yellow]Ticker [bold]{ticker_prompt}[/bold] already exists in wallet.[/bold yellow]")
        except DataFetchError as e:
            console.print(f"[bold red]Invalid ticker: [bold]{ticker_prompt}[/bold red]. Please try again.")
            continue

    if prompt:
        console.print("")
        console.print("[bold red]The following tickers will be removed from the wallet!"
                      "\nMake sure that you have no assets of that ticker in the wallet before removing them."
                      "\nOr press q to exit[/bold red]")
        console.print("")

    while prompt:
        ticker_prompt = Prompt.ask("[bold red]Enter ticker[/bold red]")

        if ticker_prompt.lower() == "q":
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
                    f"[bold red]Ticker '{ticker_prompt}' doesn't exist in wallet or contains assets, \n in such a case pls sell all assets before removing [/bold red].")
        except DataFetchError as e:
            console.print(f"[bold red]Invalid ticker: [bold]{ticker_prompt}[/bold red]. Please try again.")
            continue

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

    final_wallet_table = create_wallet_table(final_wallet, "Final Wallet", transient=False, print_info=False)

    console.print(
        Panel(Columns([create_wallet_table(started_wallet, title="Wallet", transient=False), changes_table, final_wallet_table]),
              title="Wallet Changes", border_style="bold magenta"))

    # Beautiful validation prompt with changes listed
    validation_prompt = Prompt.ask(f"[bold green]Do you want to update the profile wallet?[/bold green]",
                                   choices=["y", "n"], default="y")

    if validation_prompt == "n":
        typer.Abort()
        return

    profile_id: int = get_profile(name=profile_name).id

    if update_profile(id=profile_id, wallet=final_wallet):
        console.print(f"[bold green]Profile '[bold]{profile_name}[/bold]' wallet successfully updated![/bold green]")
    else:
        console.print(f"[bold]Error:[/bold] Unable to update profile '[bold]{profile_name}[/bold]'.\n"
                      f"Use the [underline bold green]'list-profiles'[/underline bold green] command to view available profiles.\n",
                      f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
                      style="red")


def command_clear_wallet(
        profile_name: Annotated[
            Optional[str], typer.Argument(help="The [bold]name[/bold] of the [bold]profile[/bold] to clear.")] = None
):
    profile_name = validate_and_prompt_profile_name(profile_name)

    wallet = get_profile(name=profile_name).wallet

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
        if update_profile(id=get_profile(name=profile_name).id, wallet={}):
            console.print(
                f"[bold green]Profile '[bold]{profile_name}[/bold]' wallet successfully cleared![/bold green]")
        else:
            console.print(
                f"[bold]Error:[/bold] Unable to clear profile '[bold]{profile_name}[/bold]'. Check the [underline bold green]'logs'[/underline bold green] for more details.",
                style="red")
