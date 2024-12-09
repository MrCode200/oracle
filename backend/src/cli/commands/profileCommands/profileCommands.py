import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console

from src.services.entities import Profile
from src.utils.registry import profile_registry

console = Console()

def get_profile_names():
    return [profile.name for profile in profile_registry.get().values()]  # Assuming you get names from profile_registry


def activate_profile(
        name: str = typer.Option(None, "--name", "-n", help="The name of the profile to delete.")
):
    console.print("[bold yellow]To exit type `back`[/bold yellow]")

    def ask_for_profile_name():
        profile_names = get_profile_names()

        # Loop for user input
        while True:
            name = prompt("Enter profile name: ", completer=WordCompleter(profile_names + ['back']))
            if name == "back":
                return None
            elif name in profile_names:
                return name
            else:
                console.print(f"[bold red]Error:[/bold] Profile '[bold]{name}[/bold]' not found![/bold red]")

    if name is None:
        name = ask_for_profile_name()
    if name:
        profile: Profile = profile_registry.get(name)
        if profile:
            if profile.activate():
                console.print(f"[bold green]Profile '[bold]{name}[/bold]' activated successfully![/bold green]")
            else:
                console.print(f"[bold red]Error:[/bold red] Profile '[bold]{name}[/bold]' couldn't be activated!")
        else:
            console.print(f"[bold red]Error:[/bold] Profile '[bold]{name}[/bold]' not found![/bold red]")


def deactivate_profile(
        name: str = typer.Option(None, "--name", "-n", help="The name of the profile to delete.")
):
    console.print("[bold yellow]To exit type `back`[/bold yellow]")

    def ask_for_profile_name():
        profile_names = get_profile_names()

        while True:
            name = prompt("Enter profile name: ", completer=WordCompleter(profile_names + ['back']))

            if name == "back":
                return None
            elif name in profile_names:
                return name
            else:
                console.print(f"[bold red]Error:[/bold] Profile '[bold]{name}[/bold]' not found![/bold red]")

    if name is None:
        name = ask_for_profile_name()
    if name:
        profile: Profile = profile_registry.get(name)
        if profile:
            if profile.deactivate():
                console.print(f"[bold green]Profile '[bold]{name}[/bold]' deactivated successfully![/bold green]")
            else:
                console.print(f"[bold red]Error:[/bold red] Profile '[bold]{name}[/bold]' couldn't be deactivated!\n")
        else:
            console.print(f"[bold red]Error:[/bold] Profile '[bold]{name}[/bold]' not found![/bold red]")