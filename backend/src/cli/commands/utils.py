from inspect import signature, Signature
from typing import Optional
from enum import Enum

from pydantic import TypeAdapter, ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.table import Table
from rich.box import ROUNDED

console = Console()
# TODO: Rename this file to create_edit_object
# TODO: Move convert_to_type into new file

def create_param_table(params: dict[str, any], types: Optional[dict[str, any]] = None) -> Table:
    """
    Create a table with the parameters of the object

    :param params: The parameters of the object
    :param types: The types of the parameters
    """
    param_table = Table(header_style="bold cyan", box=ROUNDED, style="bold")
    param_table.add_column("", style="dim")
    param_table.add_column("Parameter", style="bold green")
    param_table.add_column("Value", style="bold yellow")
    param_table.add_column("Type", style="bold magenta")

    i: int = 1
    for param_name, param in params.items():
        if types is not None:
            param_type: str = str(types[param_name])
        else:
            param_type: str = str(param.__class__.__name__)

        param_type_text: Text = Text(str(param_type))


        if type(param) == str:
            param: Text = Text("'" + str(param) + "'")

        param_table.add_row(str(i), param_name, str(param), param_type_text)
        i += 1

    return param_table


def create_edit_object_settings(obj: type, settings: Optional[dict[str, any]] = None):
    """
    Initializes an object with a rich console and prompts the user to change the parameters of the object.

    :param obj: The object to be initialized.
    :param settings: A dictionary of keyword arguments to be passed to the object's constructor.
                    If not provided, the function will create a dictionary with default values (excluding 'self').

    :return: A dictionary of keyword arguments to be passed to the object's constructor.
    """
    params = signature(obj).parameters

    if settings is None:
        settings: dict[str, any] = {}

        for param_name, param in params.items():
            settings[param_name] = param.default

    if settings == {}:
        return settings

    types: dict[str, any] = obj.__init__.__annotations__

    console.print(create_param_table(settings, types=types))

    console.print(Panel(
        "[bold yellow]Type the name of the [underline white]`Parameter`[/underline white] you want to change:\n"
        "When you're done, press [underline white]`enter`[/underline white]\n"
        "To view all parameters, type [underline white]`VIEW`[/underline white]\n"
        "Enums Options will be displayed.",
        title="INFO", box=ROUNDED, expand=False, border_style="bold bright_blue"
    ))

    while True:
        user_input = prompt("Parameter: ",
                            completer=WordCompleter(list(settings.keys()) + ["VIEW"],
                                                    ignore_case=True))
        if user_input == "VIEW":
            console.print(create_param_table(settings, types=types))

        elif user_input == "":
            empty_parameter_flag: bool = False

            for name, value in settings.items():
                if value == Signature.empty:
                    console.print(
                        f"[bold red]Error:[/bold red] Parameter '[underline grey]{name}[/underline grey]' is not a valid parameter for type '[underline grey]{Signature.empty}[/underline grey]'.")
                    empty_parameter_flag = True
                    break

            if not empty_parameter_flag:
                console.print(create_param_table(settings, types=types))
                confirmation = Confirm.ask(
                    "Are you sure you want to apply these changes?",
                    choices=["y", "n"],
                    default="y"
                )
                if confirmation == "y":
                    return settings

        else:
            if user_input in settings:
                param_name: str = user_input
                param_value = settings[param_name]
                param_annotation = params[param_name].annotation

                # Check if the parameter is an Enum type
                if isinstance(param_annotation, type) and issubclass(param_annotation, Enum):
                    enum_values = [member.name for member in param_annotation]
                    console.print(f"[bold green]Enum options for {param_name}[/bold green]: {', '.join(enum_values)}")

                param_value = Prompt.ask(f"New value for [bold green]{param_name}[/bold green] [bright_blue]type[{types[param_name]}]",
                                         default=str(param_value))

                try:
                    typer_adapter: TypeAdapter = TypeAdapter(types[param_name])
                    settings[param_name] = typer_adapter.validate_python(param_value)
                except ValidationError:
                    console.print(f"[bold red]Conversion Error:[/bold red] Cannot convert '[underline grey]{param_value}[/underline grey]' to '[underline grey]{types[param_name]}[/underline grey]'.")
            else:
                console.print(
                    f"[bold red]Error:[/bold red] Parameter '[underline grey]{user_input}[/underline grey]' does not exist.")
