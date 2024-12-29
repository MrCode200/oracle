from rich.columns import Columns
from rich.panel import Panel
from rich.status import Status
from rich.table import box, Table
from typer import Argument, Option
from rich.console import Console
from rich.prompt import Prompt

from typing import Annotated, Optional

from logging import getLogger

from src.cli.commands.validation import validate_and_prompt_profile_name, validate_and_prompt_tc_id, \
    validate_and_prompt_ticker_in_wallet, validate_and_prompt_interval, validate_and_prompt_weight, \
    validate_and_prompt_tc_name
from src.cli.commands.tradingComponentCommands.tradingComponentUtils import create_tc_extra_table
from src.cli.commands.utils import create_edit_object_settings, create_param_table
from src.database import TradingComponentDTO
from src.services.entities import Profile
from src.services.tradingComponents import BaseTradingComponent
from src.utils.registry import tc_registry, profile_registry

logger = getLogger("oracle.app")

console = Console()


def add_trading_component_command(
        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to add Trading Component to.")] = None,
        trading_component_name: Annotated[Optional[str], Option("-i", "--trading-component",
                                                                help="The [bold]name[/bold] of the [bold]Trading Component[/bold] to add.")] = None,
        ticker: Annotated[Optional[str], Option("-t", "--tickers",
                                                help="List of [bold]tickers[/bold] to add Trading Component to.")] = "",
        weight: Annotated[Optional[int], Option("-w", "--weight",
                                                help="The [bold]weight[/bold] of the [bold]Trading Component[/bold] to add.")] = None
):
    # Validations
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile: Profile = profile_registry.get(profile_id)

    if profile.wallet == {}:
        console.print("[bold red]Error: Wallet is empty! No Trading Component can be added.[/bold red]")
        return

    # Validate trading component name
    trading_component_name: str = validate_and_prompt_tc_name(trading_component_name)
    trading_component: BaseTradingComponent = tc_registry.get(trading_component_name)

    # Get all trading component parameters
    tc_settings: dict[str, any] = create_edit_object_settings(trading_component)

    # Prompt and Validations
    ticker: str = validate_and_prompt_ticker_in_wallet(profile.wallet, ticker)
    interval: str = validate_and_prompt_interval()
    weight: float = validate_and_prompt_weight(weight)

    # Confirm changes
    console.print(Panel(Columns(
        [create_param_table(tc_settings), create_tc_extra_table(ticker, interval, weight)]),
        expand=False))

    conformation = Prompt.ask("[bold yellow]Are you sure you want to add this Trading Component?[/bold yellow]",
                              choices=["y", "n"], default="y")

    if conformation.lower() == "n":
        return

    # Update Trading Component
    with Status("Adding Trading Component...", spinner="dots") as status:
        tc_instance = trading_component(**tc_settings)

        if profile.add_trading_component(tc_instance, weight=weight, ticker=ticker,
                                         interval=interval):
            status.update(
                f"[bold green]Trading Component '[bold]{trading_component_name}[/bold]' successfully added to profile '[bold]{profile_name}[/bold]'.")
        else:
            console.print(
                f"[bold red]Error:[/bold red] Unable to add Trading Component '[bold]{trading_component_name}[/bold]' to profile '[bold]{profile_name}[/bold]'.\n"
                f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
                style="bold red",
            )


def update_trading_component_command(
        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to add Trading Component to.")] = None,
        trading_component_id: Annotated[
            Optional[int], Argument(
                help="The [bold]id[/bold] of the [bold]Trading Component[/bold] to update.")] = None,
        ticker: Annotated[Optional[str], Option("-t", "--ticker",
                                                help="The [bold]ticker[/bold] of the [bold]Trading Component[/bold] to update.")] = None,
        interval: Annotated[Optional[str], Option("-i", "--interval",
                                                  help="The [bold]interval[/bold] of the [bold]Trading Component[/bold] to update.")] = None,
        weight: Annotated[Optional[float], Option("-w", "--weight",
                                                  help="The [bold]weight[/bold] of the [bold]Trading Component[/bold] to update.")] = None
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile: Profile = profile_registry.get(profile_id)

    trading_component_id: int = validate_and_prompt_tc_id(profile_id, trading_component_id)
    tc: TradingComponentDTO = [dto for dto in profile.trading_components if dto.id == trading_component_id][0]

    new_tc_settings: dict[str, any] = tc.settings
    console.print(Panel(
        Columns(
            [create_param_table(new_tc_settings),
             create_tc_extra_table(tc.ticker, tc.interval, str(tc.weight))]),
    )
    )

    while True:
        console.print(Panel(
            f"To edit the Trading Component, press\n"
            f"[bright_red][0][/bright_red] To save and exit\n"
            f"[blue][1][/blue] To edit parameters\n"
            f"[blue][2][/blue] To edit ticker\n"
            f"[blue][3][/blue] To edit Interval\n"
            f"[blue][4][/blue] To edit Weight\n", expand=False, title="Options", border_style="bold bright_cyan",
            style="bold"))

        option: str = input("Option: ")
        if not option.isdigit():
            console.print("Error: Invalid option.", style="bold red")
            continue
        else:
            option: int = int(option)

        if option not in [0, 1, 2, 3, 4]:
            console.print("Error: Invalid option.", style="bold red")
            continue

        match option:
            case 0:
                break
            case 1:
                new_tc_settings = create_edit_object_settings(obj=tc.instance.__class__, settings=new_tc_settings)
            case 2:
                ticker: str = validate_and_prompt_ticker_in_wallet(wallet=profile.wallet, ticker=ticker)
            case 3:
                interval: str = validate_and_prompt_interval()
            case 4:
                weight: int = validate_and_prompt_weight(weight)

    # Create Table for Extra Changes
    changes_extra_table: Table = Table(box=box.ROUNDED, style="bold", title="Extra Changes", header_style="bold cyan",
                                       show_header=True)
    changes_extra_table.add_column("", style="dim white")
    changes_extra_table.add_column("Parameter", style="bold cyan")
    changes_extra_table.add_column("Old Value", style="bold yellow")
    changes_extra_table.add_column("New Value", style="bold magenta")

    if ticker != tc.ticker and ticker is not None:
        changes_extra_table.add_row("0", "Ticker", tc.ticker, ticker)
    else:
        ticker = tc.ticker

    if interval != tc.interval and interval is not None:
        changes_extra_table.add_row("1", "Interval", tc.interval, interval)
    else:
        interval = tc.interval

    if weight != tc.weight and weight is not None:
        changes_extra_table.add_row("2", "Weight", str(tc.weight), str(weight))
    else:
        weight = tc.weight

    # Create Table for Settings Changes
    changes_setting_table: Table = Table(box=box.ROUNDED, style="bold", title="Settings Changes",
                                         header_style="bold cyan", show_header=True)
    changes_setting_table.add_column("", style="dim white")
    changes_setting_table.add_column("Parameter", style="bold cyan")
    changes_setting_table.add_column("Old Value", style="bold yellow")
    changes_setting_table.add_column("New Value", style="bold magenta")

    i = 1
    for key, value in new_tc_settings.items():
        if value != tc.settings[key]:
            changes_setting_table.add_row(str(i), key, str(tc.settings[key]), str(value))
            i += 1

    console.print(
        Columns([
            Panel(
                Columns([changes_extra_table,
                         changes_setting_table]),
                expand=False,
                title="Changes"
            ),
            Panel(
                Columns(
                    [create_param_table(new_tc_settings),
                     create_tc_extra_table(ticker, interval, weight)]),
                expand=False,
                title="Final Result"
            )
        ])
    )

    conformation = Prompt.ask("[bold yellow]Are you sure you want to add this Trading Component?[/bold yellow]",
                              choices=["y", "n"], default="y")

    if conformation.lower() == "n":
        return

    if profile.update_trading_component(
            trading_component_id=tc.id,
            name=tc.name,
            ticker=ticker,
            interval=interval,
            weight=weight,
            settings=new_tc_settings):
        console.print("[bold]Trading Component updated successfully![/bold]")
    else:
        console.print("[bold red]Error: Trading Component not updated![/bold red]")


def list_profile_trading_component_command(
        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to list Trading Components off.")] = None,
        trading_component_id: Annotated[
            Optional[int], Argument(
                help="The [bold]id[/bold] of the [bold]Trading Component[/bold] to show detailed information.")] = None
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    trading_component_id: Optional[int] = validate_and_prompt_tc_id(profile_id=profile_id, trading_component_id=trading_component_id,
                                                                    allow_none=True)

    profile: Profile = profile_registry.get(profile_id)
    trading_components = profile.trading_components

    if trading_component_id is None:
        tc_table: Table = Table(title="Trading Components", header_style="bold cyan", box=box.ROUNDED, style="bold")
        tc_table.add_column("ID", style="dim white")
        tc_table.add_column("Name", style="bold magenta")
        tc_table.add_column("Ticker", style="bold bright_yellow")
        tc_table.add_column("Interval", style="bold blue")
        tc_table.add_column("Weight", style="bold bright_cyan")

        for tc in trading_components:
            tc_table.add_row(str(tc.id), tc.name, tc.ticker, tc.interval,
                                    str(tc.weight))

        console.print(tc_table)

    else:
        tc: TradingComponentDTO = [dto for dto in trading_components if dto.id == trading_component_id][0]

        console.print(Panel(
            Columns([create_tc_extra_table(
                tc.ticker, tc.interval, tc.weight, tc_id=tc.id
            ), create_param_table(tc.settings)]),
            title=tc.name,
            border_style="bold magenta",
            box=box.ROUNDED,
            expand=False
        ))


def remove_trading_component_command(
        profile_name: Annotated[Optional[str], Argument(
            help="The [bold]name[/bold] of the [bold]profile[/bold] to add [bold]Trading Component[/bold] to.")] = None,
        trading_component_id: Annotated[
            Optional[int], Argument(help="The [bold]id[/bold] of the [bold]Trading Component[/bold] to add.")] = None
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile: Profile = profile_registry.get(profile_id)

    trading_component_id: int = validate_and_prompt_tc_id(profile_id=profile_id, trading_component_id=trading_component_id)

    conformation = Prompt.ask("[bold yellow]Are you sure you want to remove this Trading Component?[/bold yellow]",
                              choices=["y", "n"], default="y")

    if conformation.lower() != "y":
        return

    if profile.remove_trading_component(trading_component_id):
        console.print(
            f"[bold green]Trading Component '[bold]{trading_component_id}[/bold]' successfully removed from profile '[bold]{profile_name}[/bold]'.")
    else:
        console.print(
            f"[bold red]Error:[/bold red] Unable to remove Trading Component '[bold]{trading_component_id}[/bold]' from profile '[bold]{profile_name}[/bold]'.\n"
            f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
            style="bold red",
        )
