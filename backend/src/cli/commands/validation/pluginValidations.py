from typing import Optional

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import prompt
from rich.console import Console

from src.utils.registry import plugin_registry, profile_registry

console = Console()

def validate_and_prompt_plugin_name(plugin_name: Optional[str] = None):
    valid_plugin_names = [plugin.name for plugin in plugin_registry]
    while True:
        if plugin_name is None:
            plugin_name = prompt("Enter the name of the plugin: ",
                                completer=WordCompleter(valid_plugin_names, ignore_case=True))

        if plugin_name not in valid_plugin_names:
            console.print(f"[bold red]Error: Plugin '[white underline bold]{plugin_name}[/white underline bold]' not found!")
            plugin_name = None
        else:
            return plugin_name


def validate_and_prompt_plugin_id(profile_id: int, plugin_id: Optional[int] = None):
    valid_plugin_ids = [plugin.id for plugin in profile_registry.get(profile_id).plugins]
    while True:
        if plugin_id is None:
            plugin_id = prompt("Enter the id of the plugin: ",
                                completer=WordCompleter(valid_plugin_ids, ignore_case=True))

        if plugin_id not in valid_plugin_ids:
            console.print(f"[bold red]Error: Plugin '[white underline bold]{plugin_id}[/white underline bold]' not found!")
            plugin_id = None
        else:
            return plugin_id