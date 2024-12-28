from inspect import signature, Signature
from typing import Optional
import ast
from enum import Enum

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.table import Table
from rich.box import ROUNDED

console = Console()


def create_param_table(params: dict[str, any], types: Optional[dict[str, any]] = None) -> Table:
    """
    Create a table with the parameters of the object

    :param params: The parameters of the object
    :param types: The types of the parameters
    """
    print(types)
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
        param_text: Text = Text(param_type)
        param_table.add_row(str(i), param_name, str(param), param_text)
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
    params = signature(obj).parameters

    if settings is None:
        settings: dict[str, any] = {}

        for param_name, param in params.items():
            settings[param_name] = param.default

    types: dict[str, any] = {}
    for param_name, param in params.items():
        types[param_name] = param.annotation

    if settings == {}:
        return settings

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
                        f"[bold red]Error:[/bold red] Parameter '[underline grey]{name}[/underline grey]' cannot be '[underline grey]{Signature.empty}[/underline grey]' is not a valid parameter.")
                    empty_parameter_flag = True
                    break

            if not empty_parameter_flag:
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

                param_value = Prompt.ask(f"New value for [bold green]{param_name}[/bold green]:",
                                         default=str(param_value))

                try:
                    print(types[param_name])
                    settings[param_name] = convert_to_type(param_value, types[param_name], fallback=param_value)
                except (ValueError, SyntaxError) as e:
                    console.print(f"[bold red]Error:[/bold red] {e}")
            else:
                console.print(
                    f"[bold red] Parameter '[underline grey]{user_input}[/underline grey]' is not a valid parameter.[/bold red]"
                )

def convert_to_type(
        value: any,
        target_type: type,
        fallback: any = None,
        raise_exception: bool = True
) -> any:
    """
    Convert a value to a specific type.
    Uses the `ast.literal_eval` function to evaluate the value of basic types (str not included).

    Supports:
    - Enum members by name or value
    - Conversion to basic types like int, str, float, bool, etc.
    - List, Dict, Tuple and Optional as parameterized generics
    - Union of basic types

    :param value: The value to convert.
    :param target_type: The type to convert the value to.
    :param fallback: The value to return if the conversion fails.
    :param raise_exception: Whether to raise an exception if the value cannot be evaluated.
    :return: The converted value or the fallback value.
    """
    # Check if Enum
    if isinstance(target_type, type) and issubclass(target_type, Enum) and target_type is not Enum:
        valid_names = [member.name for member in target_type]
        valid_values = [member.value for member in target_type]

        if value in valid_names:
            return target_type[value]
        elif value in valid_values:
            return target_type(value)
        else:
            if raise_exception:
                raise ValueError(f"Value '{value}' is not a valid member of enum '{target_type.__name__}'.")

            return fallback

    # Turn to basic type
    if target_type == str:
        return str(value)

    try:
        evaluated_value: any = ast.literal_eval(value)
    except (ValueError, SyntaxError) as e:
        if raise_exception:
            raise e
        else:
            return fallback

    # Check if basic type
    try:
        if isinstance(evaluated_value, target_type):
            return evaluated_value
        else:
            if raise_exception:
                raise ValueError(f"Value '{value}' cannot be converted to type '{target_type}'.")

            return fallback
    except TypeError as e:
        pass

    # Check if parameterized generic
    try:
        if hasattr(target_type, "__origin__"):
            origin: type = target_type.__origin__
            if origin == list:
                item_type: type = target_type.__args__[0]
                return [convert_to_type(item, item_type) for item in evaluated_value]

            elif origin == dict:
                key_type, item_type = target_type.__args__
                return {convert_to_type(key, key_type): convert_to_type(item, item_type)
                        for key, item in evaluated_value.items()}

            elif origin == tuple:
                item_type: type = target_type.__args__[0]
                return tuple(convert_to_type(item, item_type) for item in evaluated_value)

    except Exception as e:
        if raise_exception:
            raise e
        else:
            return fallback