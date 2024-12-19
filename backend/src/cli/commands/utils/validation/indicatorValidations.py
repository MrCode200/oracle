from typing import Optional

import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.box import ROUNDED
from rich.prompt import Prompt

from src.database import get_indicator

console = Console()


def validate_and_prompt_interval() -> str:
    console.print(Panel(
        "[bold]Valid intervals: [green]m[/green]=[magenta]minute[/magenta], [green]h[/green]=[magenta]hour[/magenta], "
        "[green]d[/green]=[magenta]day[/magenta], [green]wk[/green]=[magenta]week[/magenta], [green]mo[/green]=[magenta]month[/magenta]",
        title="Valid intervals:", style="bold", box=ROUNDED))

    valid_interval: list[str] = ["m", "h", "d", "wk", "mo"]
    interval: Optional[str] = None

    while interval is None:
        interval = prompt("Enter interval accuracy: ", completer=WordCompleter(words=valid_interval))
        if interval not in valid_interval:
            console.print(f"[bold red]Error: Interval '[white underline bold]{interval}[/white underline bold]' not found!")
            interval = None

    interval_period: Optional[str] = None

    while interval_period is None:
        interval_period: str = Prompt.ask("Enter interval period: ", default="1")
        try:
            int_interval_period: int = int(interval_period)
            if int_interval_period <= 0:
                console.print(f"[bold red]Error: Interval period '[white underline bold]{interval_period}[/white underline bold]' must be greater than 0!")
                interval_period = None
        except ValueError:
            console.print(f"[bold red]Error: Interval period '[white underline bold]{interval_period}[/white underline bold]' not int!")
            interval_period = None

    return str(interval_period + interval)


def validate_and_prompt_indicator_id(profile_id: int, indicator_id: Optional[int] = None) -> Optional[int]:
    indicator_ids: list[int] = [indicator.id for indicator in get_indicator(profile_id=profile_id)]
    if indicator_id is None:
        indicator_id = prompt("Enter indicator id: ", completer=WordCompleter(words=[str(id) for id in indicator_ids]))

    if indicator_id not in indicator_ids:
        console.print(
            f"[bold red]Error: Indicator '[white underline bold]{indicator_id}[/white underline bold]' not found!")
        typer.Abort()
        return

    return indicator_id
