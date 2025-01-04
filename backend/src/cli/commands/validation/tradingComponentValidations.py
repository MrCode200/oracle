from typing import Optional

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.box import ROUNDED
from rich.prompt import Prompt

from src.cli.commands.profileCommands.profileUtils import isfloat
from src.database import get_trading_component
from src.utils.registry import tc_registry, profile_registry
from src.cli.commands.walletCommands.walletUtils import create_wallet_table

console = Console()

VALID_INTERVALS: list[str] = ['1s',
                              '1m', '3m', '5m', '15m', '30m',
                              '1h', '2h', '4h', '6h', '8h', '12h',
                              '1d', '3d',
                              '1w',
                              '1M']

valid_interval: list[str] = ["s", "m", "h", "d", "w", "M"]


def validate_and_prompt_tc_name(tc_name: Optional[str] = None) -> str:
    valid_tcs: list[str] = [name for name in tc_registry.get().keys()]

    while True:
        if tc_name is None:
            tc_name = prompt("Enter Trading Component name: ",
                             completer=WordCompleter(words=valid_tcs,
                                                     ignore_case=True))

        if tc_name not in valid_tcs:
            console.print(
                f"[bold red]Error: Trading Component '[white underline bold]{tc_name}[/white underline bold]' not found!")
            tc_name = None
        else:
            return tc_name


# TODO: improve as not all interval periods are supported
def validate_and_prompt_interval() -> str:
    console.print(Panel(
        "[bold]Valid intervals: "
        "[green]s[/green]=[magenta]second[/magenta], "
        "[green]m[/green]=[magenta]minute[/magenta], "
        "[green]h[/green]=[magenta]hour[/magenta], "
        "[green]d[/green]=[magenta]day[/magenta], "
        "[green]w[/green]=[magenta]week[/magenta], "
        "[green]M[/green]=[magenta]month[/magenta]",
        title="Valid intervals:", style="bold", box=ROUNDED, expand=False))

    interval: Optional[str] = None
    while True:
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

        final_interval: str = str(interval_period + interval)
        if final_interval in VALID_INTERVALS:
            return final_interval


def validate_and_prompt_tc_id(profile_id: int, trading_component_id: Optional[int] = None, allow_none: bool = False) -> \
Optional[int]:
    valid_tc_ids: list[str] = [str(tc.id) for tc in profile_registry.get(profile_id).trading_components]
    user_input: Optional[str] = str(trading_component_id) if trading_component_id is not None else None

    while valid_tc_ids:
        if user_input is None:
            user_input = prompt(f"Enter Trading Component id{' (Optional)' if allow_none else ''}: ",
                                completer=WordCompleter(words=[str(indi_id) for indi_id in valid_tc_ids]))

        if user_input == "" and allow_none:
            return None

        if user_input not in valid_tc_ids:
            console.print(
                f"[bold red]Error: Trading Component '[white underline bold]{trading_component_id}[/white underline bold]' not found!")
            user_input = None

        else:
            return int(user_input)


def validate_and_prompt_weight(weight: Optional[str | float] = None) -> float:
    while True:
        if weight is None:
            weight: Optional[str] = Prompt.ask("Weight", default="1")

        if not isfloat(weight):
            console.print("[bold red]Error:[/bold red] Weight must be an integer.", style="red")
            weight = None
            continue

        weight: float = float(weight)
        if weight <= 0:
            console.print("[bold red]Error:[/bold red] Weight must be greater or equal to 0.", style="red")
            weight = None
        else:
            confirmation: str = Prompt.ask(f"Add {weight} to Trading Component?", choices=["y", "n"], default="y")
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
            confirmation: str = Prompt.ask(f"Add {ticker} to Trading Component?", choices=["y", "n"], default="y")
            if confirmation == "y":
                return ticker
