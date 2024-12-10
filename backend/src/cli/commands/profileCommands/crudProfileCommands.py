from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from typer import Option

from api import fetch_info_data
from src.exceptions import DataFetchError
from src.database import delete_profile, get_profile, create_profile
from utils.registry import profile_registry

console = Console()


def get_profile_names() -> list[str]:
    return [profile.name for profile in get_profile()]


def view_wallet(wallet: dict[str, float]):
    table = Table(title="Wallet", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("", style="dim")
    table.add_column("Ticker", style="bold cyan")
    table.add_column("Current Price", style="bold green")

    i = 1
    for ticker, _ in wallet.items():
        info = fetch_info_data(ticker)
        current_price = info.get("currentPrice", None)

        if current_price is None:
            current_price = info.get("regularMarketPreviousClose", None)

        table.add_row(str(i), ticker, str(current_price) + "$")
        i += 1

    console.print(table)

def command_create_profile(
        name: str = Option(None, "--name", "-n", help="The name of the profile to create.", prompt=True),
        balance: float = Option(0, "--balance", "-b", help="The balance of the profile.", prompt=True),
        paper_balance: float = Option(0, "--paper-balance", "-p", help="The paper balance of the profile.",
                                      prompt=True)):
    wallet: dict[str, float] = {}

    # Display an introductory message with rich text
    # TODO: add teh remove [ticker] command
    console.print(Panel("[bold yellow]Enter the ticker for each asset you want to track.\n"
                        "To see your wallet type [white underline]`view-wallet`[/white underline], "
                        "and to remove a ticker type [white underline]`remove [ticker]`[/white underline].\n"
                        "To exit, type [white underline]`finish`[/white underline].", expand=False))

    while True:
        # Use rich prompt for better user interaction
        ticker_prompt = Prompt.ask("[bold green]Enter ticker[/bold green]")

        if ticker_prompt.lower() == "view-wallet":
            view_wallet(wallet)
            continue
        elif ticker_prompt.lower() == "finish":
            console.print("[bold cyan]Finished wallet creation...[/bold cyan]")
            break

        try:
            fetch_info_data(ticker_prompt)  # Assuming it fetches the data for the ticker
            wallet[ticker_prompt] = 0  # Add to wallet with a balance of 0 for now
            console.print(
                f"[bold green]Ticker '[bold]{ticker_prompt}[/bold]' added successfully to wallet![/bold green]")
        except DataFetchError as e:
            console.print(f"[bold red]Invalid ticker: [bold]{ticker_prompt}[/bold red]. Please try again.")
            continue


def command_delete_profile(
        name: str = Option(None, "--name", "-n", help="The name of the profile to delete.")
):
    # Prompt user if name is not provided
    profile_names = get_profile_names()
    if name is None:
        name = prompt("Enter profile name: ", completer=WordCompleter(profile_names))

    # Check if profile exists
    if name not in profile_names:
        console.print(
            f"[bold red]Error:[/bold red] Profile '[bold]{name}[/bold]' not found!\n"
            f"Use the [underline bold green]'list-profiles'[/underline bold green] command to view available profiles.",
            style="red",
        )
        return

    # Beautify the confirmation prompt
    confirmation_prompt = Text(
        f"[yellow]Are you sure you want to delete the profile [bold]'{name}'[/bold]? This action is irreversible.[/yellow]",
    )
    confirmation = Confirm.ask(str(confirmation_prompt), choices=["y", "n"], default="n")

    if confirmation is False:
        console.print("[bold green]Operation cancelled.[/bold green]")
        return

    if profile_registry.get(name).deactivate():
        delete_profile(name=name)
        console.print(f"[bold green]Profile '[bold]{name}[/bold]' successfully deleted![/bold green]")
    else:
        console.print(
            f"[bold]Error:[/bold] Unable to deactivate profile '[bold]{name}[/bold]'.\n"
            f"Use the [underline bold green]'list-profiles'[/underline bold green] command to view available profiles.\n",
            f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
            style="red",
        )
