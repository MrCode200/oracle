from typing import Optional

from rich.console import Console
from rich.table import Table, box

console = Console()


def create_tc_extra_table(ticker: str, interval: str, weight: int, tc_id: Optional[int] = None) -> Table:
    """
    Create a table with the extra information of the Trading Component

    :param ticker: The ticker of the Trading Component
    :param interval: The interval of the Trading Component
    :param weight: The weight of the Trading Component
    :param tc_id: The id of the Trading Component
    """
    tc_extra_table: Table = Table(header_style="bold cyan", box=box.ROUNDED, style="bold")
    tc_extra_table.add_column("", style="dim white")
    tc_extra_table.add_column("Extra", style="bold cyan")
    tc_extra_table.add_column("Value", style="bold magenta")

    tc_extra_table.add_row("0", "ID", str(tc_id)) if tc_id is not None else None
    tc_extra_table.add_row("1", "Ticker", ticker)
    tc_extra_table.add_row("2", "Interval", interval)
    tc_extra_table.add_row("3", "Weight", str(weight))

    return tc_extra_table


