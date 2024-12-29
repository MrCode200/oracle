from typing import Optional

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.box import ROUNDED
from rich.prompt import Prompt

from src.database import get_indicator
from src.utils.registry import indicator_registry
from src.cli.commands.walletCommands.walletUtils import create_wallet_table

console = Console()

valid_indicators: list[str] = [name for name in indicator_registry.get().keys()]


def validate_and_prompt_indicator_name(indicator_name: Optional[str] = None) -> str:
    while True:
        if indicator_name is None:
            indicator_name = prompt("Enter indicator name: ",
                                    completer=WordCompleter(words=valid_indicators,
                                                            ignore_case=True))

        if indicator_name not in valid_indicators:
            console.print(
                f"[bold red]Error: Indicator '[white underline bold]{indicator_name}[/white underline bold]' not found!")
            indicator_name = None
        else:
            return indicator_name


def validate_and_prompt_interval() -> str:
    console.print(Panel(
        "[bold]Valid intervals: [green]m[/green]=[magenta]minute[/magenta], [green]h[/green]=[magenta]hour[/magenta], "
        "[green]d[/green]=[magenta]day[/magenta], [green]wk[/green]=[magenta]week[/magenta], [green]mo[/green]=[magenta]month[/magenta]",
        title="Valid intervals:", style="bold", box=ROUNDED, expand=False))

    valid_interval: list[str] = ["m", "h", "d", "wk", "mo"]

    interval: Optional[str] = None
    while interval is None:
        interval = prompt("Enter interval accuracy: ",
                          completer=WordCompleter(words=valid_interval))
        if interval not in valid_interval:
            console.print(
                f"[bold red]Error: Interval '[white underline bold]{interval}[/white underline bold]' not found!")
            interval = None

    interval_period: Optional[str] = None

    while interval_period is None:
        interval_period: str = Prompt.ask("Enter interval period: ", default="1")
        try:
            int_interval_period: int = int(interval_period)

            if int_interval_period <= 0:
                console.print(
                    f"[bold red]Error: Interval period '[white underline bold]{interval_period}[/white underline bold]' must be greater than 0!")
                interval_period = None

        except ValueError:
            console.print(
                f"[bold red]Error: Interval period '[white underline bold]{interval_period}[/white underline bold]' not int!")
            interval_period = None

    return str(interval_period + interval)


def validate_and_prompt_indicator_id(profile_id: int, indicator_id: Optional[int] = None, allow_none: bool = False) -> Optional[int]:
    valid_indicator_ids: list[str] = [str(indicator.id) for indicator in get_indicator(profile_id=profile_id)]
    user_input: Optional[str] = str(indicator_id) if indicator_id is not None else None

    while valid_indicator_ids:
        if user_input is None:
            user_input = prompt(f"Enter indicator id{' (Optional)' if allow_none else ''}: ",
                                       completer=WordCompleter(words=[str(indi_id) for indi_id in valid_indicator_ids]))

        if user_input == "" and allow_none:
            return None

        if user_input not in valid_indicator_ids:
            console.print(
                f"[bold red]Error: Indicator '[white underline bold]{indicator_id}[/white underline bold]' not found!")
            user_input = None

        else:
            return int(user_input)


def validate_and_prompt_weight(weight: Optional[str | int] = None) -> int:
    while True:
        if weight is None:
            weight: Optional[str] = Prompt.ask("Weight", default="1")

        if not weight.isdigit():
            console.print("[bold red]Error:[/bold red] Weight must be an integer.", style="red")
            weight = None
            continue

        weight: int = int(weight)
        if weight <= 0:
            console.print("[bold red]Error:[/bold red] Weight must be greater or equal to 0.", style="red")
            weight = None
        else:
            confirmation: str = Prompt.ask(f"Add {weight} to indicator?", choices=["y", "n"], default="y")
            if confirmation == "y":
                return weight



def validate_and_prompt_ticker_in_wallet(wallet: dict[str, float], ticker: Optional[str] = None) -> str:
    console.print(create_wallet_table(wallet=wallet, title="Wallet"))

    tickers_in_wallet: list[str] = list(wallet.keys())
    while True:
        if ticker is None:
            ticker: Optional[str] = prompt("Ticker: ", completer=WordCompleter(tickers_in_wallet, ignore_case=True))

        if ticker not in tickers_in_wallet:
            console.print(f"[bold red] Ticker is not in Wallet! [/bold red]")
            ticker = None
        else:
            console.print(f"[bold green] Ticker added! [/bold green]")
            confirmation: str = Prompt.ask(f"Add {ticker} to indicator?", choices=["y", "n"], default="y")
            if confirmation == "y":
                return ticker