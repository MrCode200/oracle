from rich.console import Console
from rich.table import Table

from src.utils.registry import plugin_registry

console = Console()


def list_plugins_command():
    console.print("[bold green]Available plugins:[/bold green]")

    # Create a table to display the Plugins
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Number", style="dim")
    table.add_column("Plugin Name")

    i: int = 1
    for plugin in plugin_registry.get().keys():
        table.add_row(str(i), plugin)
        i += 1

    console.print(table)
