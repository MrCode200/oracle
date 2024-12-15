from typing import Optional

import typer

from src.database.operations.profileOperations import get_profile
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import prompt
from rich.console import Console

console = Console()

def get_profile_names() -> list[str]:
    return [profile.name for profile in get_profile()]

def validate_and_prompt_profile_name(profile_name: Optional[str] = None) -> Optional[str]:
    profile_names = get_profile_names()
    if profile_name is None:
        profile_name = prompt("Enter profile name: ", completer=WordCompleter(words=profile_names))

    if profile_name not in profile_names:
        console.print(f"[bold red]Error: Profile '[white underline bold]{profile_name}[/white underline bold]' not found!")
        typer.Abort()
    return profile_name
