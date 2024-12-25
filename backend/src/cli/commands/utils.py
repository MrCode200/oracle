from inspect import signature
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.table import Table
from rich.box import ROUNDED

console = Console()

def create_param_table(class_kwargs: dict[str, any]) -> Table:
    """
    Create a table with the parameters of the object

    :param class_kwargs: The parameters of the object
    """
    param_table = Table(header_style="bold cyan", box=ROUNDED, style="bold")
    param_table.add_column("", style="dim")
    param_table.add_column("Parameter", style="bold green")
    param_table.add_column("Value", style="bold yellow")
    param_table.add_column("Type", style="bold magenta")

    i: int = 1
    for param_name, param in class_kwargs.items():
        param_table.add_row(str(i), param_name, str(param), str(param.__class__.__name__))
        i += 1

    return param_table

def create_edit_object_settings(obj: object, settings: Optional[dict[str, any]] = None):
    """
    Initializes an object with a rich console and prompts the user to change the parameters of the object.

    :param obj: The object to be initialized.
    :param settings: A dictionary of keyword arguments to be passed to the object's constructor.
                               If not provided, the function will create a dictionary with default values (excluding 'self').

    :return: A dictionary of keyword arguments to be passed to the object's constructor.
    """
    params = signature(obj.__init__).parameters

    if settings is None:
        settings: dict[str, any] = {}

        for param_name, param in params.items():
            if param_name != "self":
                settings[param_name] = param.default

    console.print(create_param_table(settings))

    console.print(Panel(
        "[bold yellow]Type the name of the [underline white]`Parameter`[/underline white] you want to change:\n"
        "When you're done, press [underline white]`enter`[/underline white]\n"
        "To view all parameters, type [underline white]`VIEW`[/underline white]\n"
        "For bools, [underline white]1 is True[/underline white] and [underline white]0 is False",
        title="INFO", box=ROUNDED, expand=False, border_style="bold bright_blue"
    ))

    while True:
        param_name = prompt("Parameter: ",
                            completer=WordCompleter(list(settings.keys()) + ["VIEW"], ignore_case=True))
        if param_name == "VIEW":
            console.print(create_param_table(settings))
        elif param_name == "":
            break

        else:
            if param_name in settings:
                param_value = Prompt.ask(f"New value for [bold green]{param_name}[/bold green]:",
                                         default=str(settings[param_name]))

                if params[param_name].annotation == bool:
                    if param_value not in ["1", "0"]:
                        console.print(
                            f"[bold red]Error:[/bold red] Parameter '[underline grey]{param_name}[/underline grey]' must be 1 or 0.",
                            style="red")
                        continue
                    param_value = True if param_value == "1" else False

                elif params[param_name].annotation == int:
                    try:
                        param_value = int(param_value)
                    except ValueError:
                        console.print(
                            f"[bold red]Error:[/bold red] Parameter '[underline grey]{param_name}[/underline grey]' must be an integer.",
                            style="red")
                        continue

                settings[param_name] = param_value
            else:
                console.print(
                    f"[bold red] Parameter '[underline grey]{param_name}[/underline grey]' is not a valid parameter.[/bold red]"
                )

    return settings