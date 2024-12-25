from typing import Optional

from rich.console import Console
from rich.table import Table, box

console = Console()


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


