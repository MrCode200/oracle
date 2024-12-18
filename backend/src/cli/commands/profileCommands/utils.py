from typing import Optional, Type

import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console

from src.database import get_indicator
from src.database.operations.profileOperations import get_profile
from src.services.entities import Status

console = Console()


def get_profile_names() -> list[str]:
    return [profile.name for profile in get_profile()]


def validate_and_prompt_profile_name(profile_name: Optional[str] = None) -> Optional[str]:
    profile_names = get_profile_names()
    if profile_name is None:
        profile_name = prompt("Enter profile name: ", completer=WordCompleter(words=profile_names))

    if profile_name not in profile_names:
        console.print(
            f"[bold red]Error: Profile '[white underline bold]{profile_name}[/white underline bold]' not found!")
        typer.Abort()
    return profile_name


def validate_and_prompt_status(status: Optional[str] = None) -> Optional[Type[Status]]:
    status_names: list[str] = [status.name for status in Status]
    if status is None:
        status = prompt("Enter status: ", completer=WordCompleter(words=[status.name for status in Status]))

    if status not in status_names:
        console.print(f"[bold red]Error: Status '[white underline bold]{status}[/white underline bold]' not found!")
        typer.Abort()
        return

    return Status[status]


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
