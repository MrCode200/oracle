from typing import Optional, Type

import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console

from src.database import get_indicator

console = Console()

def validate_and_prompt_interval(interval: str) -> str:
    ...

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