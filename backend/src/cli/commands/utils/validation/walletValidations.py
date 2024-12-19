from rich.console import Console

from src.database import get_profile

console = Console()


def validate_ticker_in_wallet(tickers: list[str] | str, wallet: dict[str, float]) -> bool:
    if isinstance(tickers, str):
        tickers = [tickers]

    for ticker in tickers:
        if ticker not in wallet:
            console.print(f"[bold red]Error: Ticker '[white underline bold]{ticker}[/white underline bold]' not found!")
            return False

    return True
