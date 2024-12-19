from inspect import signature

from prompt_toolkit import prompt
from rich.columns import Columns
from rich.panel import Panel
from prompt_toolkit.completion import WordCompleter
from rich.status import Status
from rich.table import box, Table
from typer import Argument, Option
from rich.console import Console
from rich.prompt import Prompt

from typing import Annotated, Optional

from logging import getLogger

from src.cli.commands.utils import create_wallet_table

logger = getLogger("oracle.app")

from src.cli.commands.utils import validate_and_prompt_profile_name, validate_and_prompt_indicator_id, \
    validate_ticker_in_wallet, validate_and_prompt_interval, create_param_table
from src.database import get_profile, ProfileDTO
from src.utils.registry import indicator_registry, profile_registry

console = Console()


def add_indicator_command(
        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to add indicator to.")] = None,
        indicator_name: Annotated[Optional[str], Option("-i", "--indicator",
                                                        help="The [bold]name[/bold] of the [bold]indicator[/bold] to add.")] = None,
        indicator_ticker: Annotated[Optional[str], Option("-t", "--tickers",
                                                          help="List of [bold]tickers[/bold] to add indicator to.")] = ""
):
    # Validations
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile: ProfileDTO = get_profile(id=profile_id)

    validate_ticker_in_wallet(wallet=profile.wallet, tickers=indicator_ticker) if indicator_ticker is not indicator_ticker else None

    if indicator_name is None:
        indicator_name = prompt("Enter indicator name: ",
                                completer=WordCompleter(words=[name for name in indicator_registry.get().keys()],
                                                        ignore_case=True))

    if indicator_name not in indicator_registry.get().keys():
        console.print(
            f"[bold red]Error: Indicator '[white underline bold]{indicator_name}[/white underline bold]' not found!")

    # Get all indicator parameters
    class_kwargs: dict[str, any] = {}
    indi_args = signature(indicator_registry.get(indicator_name).__init__).parameters

    for param_name, param in indi_args.items():
        if param_name != "self":
            class_kwargs[param_name] = param.default

    console.print(create_param_table(class_kwargs))

    console.print(Panel(
        "[bold yellow]Type the name of the `Parameter` you want to change:\n"
        "When you're done, press `enter`\n"
        "To view all parameters, type `VIEW`[/bold yellow]\n"
        "For bools, 1 is True and 0 is False",
        title="INFO", box=box.ROUNDED, style="bold cyan"
    ))

    # Loop and prompt for changing parameters
    while True:
        param_name = prompt("Parameter: ", completer=WordCompleter(list(class_kwargs.keys()) + ["VIEW"]))
        if param_name == "VIEW":
            console.print(create_param_table(class_kwargs))
        elif param_name == "":
            break

        else:
            if param_name in class_kwargs:
                param_value = Prompt.ask(f"New value for [bold green]{param_name}[/bold green]:",
                                         default=str(class_kwargs[param_name]))

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

                class_kwargs[param_name] = param_value
            else:
                console.print(
                    f"[bold red] Parameter '[underline grey]{param_name}[/underline grey]' is not a valid parameter.[/bold red]"
                )


    # Loop and prompt for adding tickers to indicator
    console.print(create_wallet_table(wallet=profile.wallet, title="Wallet"))
    console.print(Panel(
        f"[bold yellow]Type the name of the [bold underline grey]ticker[/bold underline grey] you want to add this indicator to\n."
        f"Type it again to [bold underline grey]remove[/bold underline grey] it!\n"
        f"Press [bold underline green]enter[/bold underline green] to finish[/bold yellow]", title="INFO",
        style="bold cyan", box=box.ROUNDED))

    if indicator_ticker == "":
        while True:
            ticker_prompt = prompt("Ticker: ", completer=WordCompleter(profile.wallet.keys(), ignore_case=True))
            if validate_ticker_in_wallet(ticker_prompt, profile.wallet):
                indicator_ticker = ticker_prompt
                console.print(f"[bold green] Ticker added! [/bold green]")
                break
            else:
                console.print(f"[bold red] Ticker is not in Wallet! [/bold red]")
                continue

    # Prompt and Validate interval
    interval: str = validate_and_prompt_interval()

    while True:
        weight: str = Prompt.ask("Weight", default="1")
        try:
            weight: int = int(weight)
            if weight < 0:
                console.print("[bold red]Error:[/bold red] Weight must be greater than 0.", style="red")
            else:
                break
        except ValueError:
            console.print("[bold red]Error:[/bold red] Weight must be an integer.", style="red")
            continue

    extra_table = Table(header_style="bold cyan", border_style="bold", box=box.ROUNDED, style="bold")
    extra_table.add_column("Extra Parameters", style="bold green")
    extra_table.add_column("Value", style="bold yellow")

    extra_table.add_row("Tickers", indicator_ticker)
    extra_table.add_row("Interval", interval)
    extra_table.add_row("Weight", str(weight))

    # Confirm changes
    console.print(Panel(Columns([create_param_table(class_kwargs), extra_table])))

    conformation = Prompt.ask("[bold yellow]Are you sure you want to add this indicator?[/bold yellow]",
                              choices=["y", "n"], default="y")

    if conformation.lower() == "n":
        return

    # Update Indicator
    with Status("Adding Indicator...", spinner="dots") as status:
        try:
            indicator = indicator_registry.get(indicator_name)(**class_kwargs)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}", style="red")
            logger.warning(f"Error Creating Instance of indicator {indicator_name} (cli): {e}")
            return

        # Success or failure message with proper styling
        if profile_registry.get(profile_id).add_indicator(indicator, weight=weight, ticker=indicator_ticker,
                                                            interval=interval):
            status.update(
                f"[bold green]Indicator '[bold]{indicator_name}[/bold]' successfully added to profile '[bold]{profile_name}[/bold]'.")
        else:
            console.print(
                f"[bold red]Error:[/bold red] Unable to add indicator '[bold]{indicator_name}[/bold]' to profile '[bold]{profile_name}[/bold]'.\n"
                f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
                style="bold red",
            )


#TODO: add update indicator command
def update_indicator_command(
        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to add indicator to.")] = None,
        indicator_id: Annotated[
            Optional[int], Option(help="The [bold]id[/bold] of the [bold]indicator[/bold] to update.")] = None
):
    ...


def list_profile_indicators_command(
        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to add indicator to.")] = None
):
    ...


def remove_indicator_command(
        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to add indicator to.")] = None,
        indicator_id: Annotated[
            Optional[int], Option(help="The [bold]id[/bold] of the [bold]indicator[/bold] to add.")] = None
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    indicator_id: int = validate_and_prompt_indicator_id(profile_id=profile_id, indicator_id=indicator_id)

    ...
