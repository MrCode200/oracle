from typing import Optional
from inspect import signature

from rich.console import Console
from rich.table import Table, box
from rich.panel import Panel
from rich.prompt import Prompt
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from src.services.entities import IndicatorBase

console = Console()

def create_indicator_param_table(class_kwargs: dict[str, any]) -> Table:
    """
    Create a table with the parameters of the indicator

    :param class_kwargs: The parameters of the indicator
    """
    param_table = Table(header_style="bold cyan", box=box.ROUNDED, style="bold")
    param_table.add_column("", style="dim")
    param_table.add_column("Parameter", style="bold green")
    param_table.add_column("Value", style="bold yellow")
    param_table.add_column("Type", style="bold magenta")

    i: int = 1
    for param_name, param in class_kwargs.items():
        param_table.add_row(str(i), param_name, str(param), str(param.__class__.__name__))
        i += 1

    return param_table


# TODO: add this to the crud indicator Commands
def create_indicator_extra_table(ticker: str, interval: str, weight: int, id: Optional[int] = None) -> Table:
    """
    Create a table with the extra information of the indicator

    :param ticker: The ticker of the indicator
    :param interval: The interval of the indicator
    :param weight: The weight of the indicator
    :param id: The id of the indicator
    """
    indicator_extra_table: Table = Table(header_style="bold cyan", box=box.ROUNDED, style="bold")
    indicator_extra_table.add_column("", style="dim white")
    indicator_extra_table.add_column("Extra", style="bold cyan")
    indicator_extra_table.add_column("Value", style="bold magenta")

    indicator_extra_table.add_row("0", "ID", str(id)) if id is not None else None
    indicator_extra_table.add_row("1", "Ticker", ticker)
    indicator_extra_table.add_row("2", "Interval", interval)
    indicator_extra_table.add_row("3", "Weight", str(weight))

    return indicator_extra_table


def create_edit_indicator_settings(indicator: IndicatorBase, indicator_settings: Optional[dict[str, any]] = None):
    indi_args = signature(indicator.__init__).parameters

    if indicator_settings is None:
        indicator_settings: dict[str, any] = {}

        for param_name, param in indi_args.items():
            if param_name != "self":
                indicator_settings[param_name] = param.default

    console.print(create_indicator_param_table(indicator_settings))

    console.print(Panel(
        "[bold yellow]Type the name of the [underline white]`Parameter`[/underline white] you want to change:\n"
        "When you're done, press [underline white]`enter`[/underline white]\n"
        "To view all parameters, type [underline white]`VIEW`[/underline white]\n"
        "For bools, [underline white]1 is True[/underline white] and [underline white]0 is False",
        title="INFO", box=box.ROUNDED, expand=False
    ))

    while True:
        param_name = prompt("Parameter: ",
                            completer=WordCompleter(list(indicator_settings.keys()) + ["VIEW"], ignore_case=True))
        if param_name == "VIEW":
            console.print(create_indicator_param_table(indicator_settings))
        elif param_name == "":
            break

        else:
            if param_name in indicator_settings:
                param_value = Prompt.ask(f"New value for [bold green]{param_name}[/bold green]:",
                                         default=str(indicator_settings[param_name]))

                if indi_args[param_name].annotation == bool:
                    if param_value not in ["1", "0"]:
                        console.print(
                            f"[bold red]Error:[/bold red] Parameter '[underline grey]{param_name}[/underline grey]' must be 1 or 0.",
                            style="red")
                        continue
                    param_value = True if param_value == "1" else False

                elif indi_args[param_name].annotation == int:
                    try:
                        param_value = int(param_value)
                    except ValueError:
                        console.print(
                            f"[bold red]Error:[/bold red] Parameter '[underline grey]{param_name}[/underline grey]' must be an integer.",
                            style="red")
                        continue

                indicator_settings[param_name] = param_value
            else:
                console.print(
                    f"[bold red] Parameter '[underline grey]{param_name}[/underline grey]' is not a valid parameter.[/bold red]"
                )

    return indicator_settings