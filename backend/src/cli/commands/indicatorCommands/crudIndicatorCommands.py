from rich.columns import Columns
from rich.panel import Panel
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.status import Status
from rich.table import box, Table
from typer import Argument, Option
from rich.console import Console
from rich.prompt import Prompt

from typing import Annotated, Optional

from logging import getLogger

logger = getLogger("oracle.app")

from src.cli.commands.validation import validate_and_prompt_profile_name, validate_and_prompt_indicator_id, \
    validate_and_prompt_ticker_in_wallet, validate_and_prompt_interval, validate_and_prompt_weight, \
    validate_and_prompt_indicator_name
from src.cli.commands.indicatorCommands.indicatorUtils import create_indicator_extra_table
from src.cli.commands.utils import create_edit_object_settings, create_param_table
from src.database import IndicatorDTO
from src.services.entities import Profile
from src.utils.registry import indicator_registry, profile_registry

console = Console()


def add_indicator_command(
        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to add indicator to.")] = None,
        indicator_name: Annotated[Optional[str], Option("-i", "--indicator",
                                                        help="The [bold]name[/bold] of the [bold]indicator[/bold] to add.")] = None,
        ticker: Annotated[Optional[str], Option("-t", "--tickers",
                                                help="List of [bold]tickers[/bold] to add indicator to.")] = "",
        interval: Annotated[Optional[str], Option("-i", "--interval",
                                                  help="The [bold]interval[/bold] of the [bold]indicator[/bold] to add.")] = None,
        weight: Annotated[Optional[int], Option("-w", "--weight",
                                                help="The [bold]weight[/bold] of the [bold]indicator[/bold] to add.")] = None
):
    # Validations
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile: Profile = profile_registry.get(profile_id)

    if profile.wallet == {}:
        console.print("[bold red]Error: Wallet is empty! No Indicator can be added.[/bold red]")
        return

    # Validate indicator_name
    indicator_name: str = validate_and_prompt_indicator_name(indicator_name)

    # Get all indicator parameters
    indicator_settings: dict[str, any] = create_edit_object_settings(indicator_name)

    # Prompt and Validations
    ticker: str = validate_and_prompt_ticker_in_wallet(ticker)
    interval: str = validate_and_prompt_interval(interval)
    weight: float = validate_and_prompt_weight(weight)

    # Confirm changes
    console.print(Panel(Columns(
        [create_param_table(indicator_settings), create_indicator_extra_table(ticker, interval, weight)]),
        expand=False))

    conformation = Prompt.ask("[bold yellow]Are you sure you want to add this indicator?[/bold yellow]",
                              choices=["y", "n"], default="y")

    if conformation.lower() == "n":
        return

    # Update Indicator
    with Status("Adding Indicator...", spinner="dots") as status:
        indicator = indicator_registry.get(indicator_name)(**indicator_settings)

        if profile.add_indicator(indicator, weight=weight, ticker=ticker,
                                 interval=interval):
            status.update(
                f"[bold green]Indicator '[bold]{indicator_name}[/bold]' successfully added to profile '[bold]{profile_name}[/bold]'.")
        else:
            console.print(
                f"[bold red]Error:[/bold red] Unable to add indicator '[bold]{indicator_name}[/bold]' to profile '[bold]{profile_name}[/bold]'.\n"
                f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
                style="bold red",
            )


def update_indicator_command(
        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to add indicator to.")] = None,
        indicator_id: Annotated[
            Optional[int], Option("-id", "--indicator-id",help="The [bold]id[/bold] of the [bold]indicator[/bold] to update.")] = None,
        ticker: Annotated[Optional[str], Option("-t", "--ticker",
                                                help="The [bold]ticker[/bold] of the [bold]indicator[/bold] to update.")] = None,
        interval: Annotated[Optional[str], Option("-i", "--interval",
                                                  help="The [bold]interval[/bold] of the [bold]indicator[/bold] to update.")] = None,
        weight: Annotated[Optional[int], Option("-w", "--weight",
                                                help="The [bold]weight[/bold] of the [bold]indicator[/bold] to update.")] = None
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile = profile_registry.get(profile_id)

    indicator_id: int = validate_and_prompt_indicator_id(indicator_id)
    indicator: IndicatorDTO = [dto for dto in profile.indicators if dto.id == indicator_id][0]

    new_indicator_settings: dict[str, any] = indicator.settings
    while True:
        console.print(Panel(
            f"To edit indicator press\n"
            f"[0] To save and exit\n"
            f"[1] To edit parameters\n"
            f"[2] To edit ticker\n"
            f"[3] To edit Interval\n"
            f"[4] To edit Weight\n", expand=False))

        option: int = input()
        if option not in [0, 1, 2, 3, 4]:
            continue

        match option:
            case 0:
                break
            case 1:
                new_indicator_settings = create_edit_object_settings(indicator_name=indicator.name,
                                                                     indicator_settings=new_indicator_settings)
            case 2:
                ticker: str = validate_and_prompt_ticker_in_wallet(wallet=profile.wallet, ticker=ticker)
            case 3:
                interval: str = validate_and_prompt_interval(interval)
            case 4:
                weight: int = validate_and_prompt_weight(weight)

    # Create Table for Extra Changes
    changes_extra_table: Table = Table(box=box.ROUNDED, style="bold", title="Extra Changes", header_style="bold cyan",
                                       show_header=True)
    changes_extra_table.add_column("", style="dim white")
    changes_extra_table.add_column("Parameter", style="bold cyan")
    changes_extra_table.add_column("Old Value", style="bold yellow")
    changes_extra_table.add_column("New Value", style="bold magenta")

    if ticker != indicator.ticker:
        changes_extra_table.add_row("0", "Ticker", indicator.ticker, ticker)
    if interval != indicator.interval:
        changes_extra_table.add_row("1", "Interval", indicator.interval, interval)
    if weight != indicator.weight:
        changes_extra_table.add_row("2", "Weight", indicator.weight, weight)

    # Create Table for Settings Changes
    changes_setting_table: Table = Table(box=box.ROUNDED, style="bold", title="Settings Changes",
                                         header_style="bold cyan", show_header=True)
    changes_setting_table.add_column("", style="dim white")
    changes_setting_table.add_column("Parameter", style="bold cyan")
    changes_setting_table.add_column("Old Value", style="bold yellow")
    changes_setting_table.add_column("New Value", style="bold magenta")

    i = 1
    for key, value in new_indicator_settings.items():
        if value != indicator.settings[key]:
            changes_setting_table.add_row(str(i), key, str(indicator.settings[key]), str(value))
            i += 1

    console.print(
        Panel(
            Columns(
                [changes_extra_table,
                 changes_setting_table],
                expand=False,
                title="Changes"
            )
        )
    )

    console.print(
        Panel(
            Columns(
                [create_param_table(new_indicator_settings),
                 create_indicator_extra_table(ticker, interval, weight)]),
            expand=False,
            title="Final Result"
        )
    )

    conformation = Prompt.ask("[bold yellow]Are you sure you want to add this indicator?[/bold yellow]",
                              choices=["y", "n"], default="y")

    if conformation.lower() == "n":
        return

    if profile.update_indicator(
            indicator_id=indicator.id,
            name=indicator.name,
            ticker=ticker,
            interval=interval,
            weight=weight,
            settings=new_indicator_settings):
        console.print("[bold]Indicator updated successfully![/bold]")
    else:
        console.print("[bold red]Error: Indicator not updated![/bold red]")


def list_profile_indicators_command(
        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to add indicator to.")] = None,
        indicator_id: Annotated[
            Optional[int], Option("--indicator-id", "-id",
                                  help="The [bold]id[/bold] of the [bold]indicator[/bold] to add.")] = None
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    indicator_id: Optional[int] = validate_and_prompt_indicator_id(profile_id=profile_id, indicator_id=indicator_id)

    profile = profile_registry.get(profile_id)
    indicators = profile.indicators

    if indicator_id is None:
        indicator_table: Table = Table(title="Indicators", header_style="bold cyan", box=box.ROUNDED, style="bold")
        indicator_table.add_column("ID", style="dim white")
        indicator_table.add_column("Name", style="bold magenta")
        indicator_table.add_column("Ticker", style="bold bright_yellow")
        indicator_table.add_column("Interval", style="bold blue")
        indicator_table.add_column("Weight", style="bold bright_cyan")

        for indicator in indicators:
            indicator_table.add_row(str(indicator.id), indicator.name, indicator.ticker, indicator.interval,
                                    str(indicator.weight))

        console.print(indicator_table)

    else:
        indicator: IndicatorDTO = [dto for dto in indicators if dto.id == indicator_id][0]

        console.print(Panel(
            Columns([create_indicator_extra_table(
                indicator.ticker, indicator.interval, indicator.weight, id=indicator.id
            ), create_param_table(indicator.settings)]),
            title=indicator.name,
            border_style="bold magenta",
            box=box.ROUNDED,
            expand=False
        ))


def remove_indicator_command(
        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to add indicator to.")] = None,
        indicator_id: Annotated[
            Optional[int], Option(help="The [bold]id[/bold] of the [bold]indicator[/bold] to add.")] = None
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile = profile_registry.get(profile_id)

    indicator_id: int = validate_and_prompt_indicator_id(profile_id=profile_id, indicator_id=indicator_id)

    conformation = Prompt.ask("[bold yellow]Are you sure you want to remove this indicator?[/bold yellow]",
                              choices=["y", "n"], default="y")

    if conformation.lower() != "y":
        return

    if profile.remove_indicator(indicator_id):
        console.print(
            f"[bold green]Indicator '[bold]{indicator_id}[/bold]' successfully removed from profile '[bold]{profile_name}[/bold]'.")
    else:
        console.print(
            f"[bold red]Error:[/bold red] Unable to remove indicator '[bold]{indicator_id}[/bold]' from profile '[bold]{profile_name}[/bold]'.\n"
            f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
            style="bold red",
        )
