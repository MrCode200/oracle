from typing import Optional

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console

from src.constants import VALID_TICKERS

console = Console()

def validate_and_prompt_ticker(ticker: Optional[str] = None) -> str:
    while True:
        if ticker is None:
            ticker: Optional[str] = prompt("Ticker: ", completer=WordCompleter(list(VALID_TICKERS.keys()), ignore_case=True))

        if ticker not in VALID_TICKERS.keys():
            console.print(f"[bold red] Ticker is not in list! [/bold red]")
            ticker = None
        else:
            console.print(f"[bold green] Ticker added! [/bold green]")
            break

    return ticker
