import logging
from typing import Optional

from rich import box
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from src.api import fetch_ticker_price

console = Console()

logger = logging.getLogger("oracle.app")


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

            current_price: Optional[float] = fetch_ticker_price(ticker)

            if current_price is None:
                invalid_tickers.append(ticker)
            else:
                holding_value: float = current_price * quantity

                final_wallet_table.add_row(str(i), ticker, str(quantity), str(current_price) + "$",
                                           str(holding_value) + "$")
            i += 1

        progress.update(final_wallet_task, advance=1, description="Done!")

    for ticker in invalid_tickers:
        logger.warning(f"{ticker} has been identified as an invalid ticker. Skipping...")
        console.print(f"[bold yellow] {ticker} has been identified as an invalid ticker. Skipping...[/bold yellow]") if print_info else None
        wallet.pop(ticker)

    if print_info and invalid_tickers:
        console.print(f"[bold red]Update wallet to remove invalid tickers![/bold red]")

    return final_wallet_table