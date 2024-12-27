from rich.console import Console
from rich.table import Table
from src.utils.registry import indicator_registry

console = Console()

def list_indicators_command():
    console.print("[bold green]Available algorithms:[/bold green]")

    # Create a table to display the indicators
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Number", style="dim")
    table.add_column("Indicator Name")

    i: int = 1
    for indicator in indicator_registry.get().keys():
        table.add_row(str(i), indicator)
        i += 1

    console.print(table)