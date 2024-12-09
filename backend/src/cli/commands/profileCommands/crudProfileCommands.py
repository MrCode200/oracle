from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.prompt import Confirm
from rich.text import Text
from typer import Option

from src.database import delete_profile, get_profile
from utils.registry import profile_registry

console = Console()


def get_profile_names() -> list[str]:
    return [profile.name for profile in get_profile()]

def command_delete_profile(
        name: str = Option(None, "--name", "-n", help="The name of the profile to delete.")
):
    # Prompt user if name is not provided
    profile_names = get_profile_names()
    if name is None:
        name = prompt("Enter profile name: ", completer=WordCompleter(profile_names))

    # Check if profile exists
    if name not in profile_names:
        console.print(
            f"[bold red]Error:[/bold red] Profile '[bold]{name}[/bold]' not found!\n"
            f"Use the [underline bold green]'list-profiles'[/underline bold green] command to view available profiles.",
            style="red",
        )
        return

    # Beautify the confirmation prompt
    confirmation_prompt = Text(
        f"[yellow]Are you sure you want to delete the profile [bold]'{name}'[/bold]? This action is irreversible.[/yellow]",
    )
    confirmation = Confirm.ask(str(confirmation_prompt), choices=["y", "n"], default="n")

    if confirmation is False:
        console.print("[bold green]Operation cancelled.[/bold green]")
        return

    if profile_registry.get(name).deactivate():
        delete_profile(name=name)
        console.print(f"[bold green]Profile '[bold]{name}[/bold]' successfully deleted![/bold green]")
    else:
        console.print(
            f"[bold]Error:[/bold] Unable to deactivate profile '[bold]{name}[/bold]'.\n"
            f"Use the [underline bold green]'list-profiles'[/underline bold green] command to view available profiles.\n",
            f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
            style="red",
        )
