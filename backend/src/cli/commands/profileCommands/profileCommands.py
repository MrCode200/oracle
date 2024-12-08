import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console

from src.cli.commands import crud_profile_app
from src.services.entities import Profile
from src.utils.registry import profile_registry

# Initialize the console for rich styling
console = Console()

# Simulate a function that lists all profiles for autocompletion
def get_profile_names():
    return [profile.name for profile in profile_registry.get().values()]  # Assuming you get names from profile_registry


@crud_profile_app.command(name="activate", help="Activates a profile.")
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
            elif name == "list profiles":
                console.print("[bold cyan]Listing all profiles...[/bold cyan]")
                crud_profile_app(["list-profiles"])
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


@crud_profile_app.command(name="deactivate", help="Deactivates a profile.")
def deactivate_profile(
        name: str = typer.Option(None, "--name", "-n", help="The name of the profile to delete.")
):
    console.print("[bold yellow]For a list of all profiles type `list profiles`, to exit type `back`[/bold yellow]")

    def ask_for_profile_name():
        profile_names = get_profile_names()
        completer = WordCompleter(profile_names + ["list profiles", "back"], ignore_case=True)

        # Loop for user input
        while True:
            name = prompt("Enter profile name: ", completer=WordCompleter(profile_names + ['back']))

            if name == "back":
                return None
            elif name == "list profiles":
                console.print("[bold cyan]Listing all profiles...[/bold cyan]")
                crud_profile_app(["list-profiles"])
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