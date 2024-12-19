from rich.console import Console

from src.database.operations.profileOperations import get_profile

console = Console()


def validate_ticker_in_wallet(tickers: list[str] | str, profile_id: int) -> bool:
    wallet = get_profile(id=profile_id).wallet

    if isinstance(tickers, str):
        tickers = [tickers]

    for ticker in tickers:
        if ticker not in wallet:
            console.print(f"[bold red]Error: Ticker '[white underline bold]{ticker}[/white underline bold]' not found!")
            return False

    return True
