from typing import Optional, Type

import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console

from src.database.operations.profileOperations import get_profile
from src.services.entities import Status

console = Console()

valid_statuses: list[str] = [status.name for status in Status if status.value < Status.UNKNOWN_ERROR.value]

def validate_and_prompt_profile_name(profile_name: Optional[str] = None) -> Optional[int]:
    profile_names = [profile.name for profile in get_profile()]

    while True:
        if profile_name is None:
            profile_name = prompt("Enter profile name: ", completer=WordCompleter(words=profile_names))

        if profile_name in profile_names:
            return get_profile(name=profile_name).id
        else:
            console.print(
                f"[bold red]Error: Profile '[white underline bold]{profile_name}[/white underline bold]' not found!")
            profile_name = None

def validate_and_prompt_status(status: Optional[str] = None) -> Optional[Type[Status]]:
    while True:
        if status is None:
            status = prompt("Enter status: ", completer=WordCompleter(words=valid_statuses, ignore_case=True))

        if status in valid_statuses:
            return Status[status]
        else:
            console.print(f"[bold red]Error: Status '[white underline bold]{status}[/white underline bold]' not found!")
            status = None