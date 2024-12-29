from typing import Annotated
from logging import getLogger

from rich.panel import Panel
from rich.prompt import Prompt
from rich.console import Console
from rich.status import Status
from rich.table import Table
from typer import Argument, Option

from src.database import PluginDTO
from src.utils.registry import plugin_registry, profile_registry
from src.cli.commands.validation import validate_and_prompt_profile_name, validate_and_prompt_plugin_name, \
    validate_and_prompt_plugin_id
from src.services.plugin import BasePlugin, PluginJob
from src.cli.commands.utils import create_edit_object_settings, create_param_table

console = Console()
logger = getLogger("oracle.app")


def add_plugin_command(
        profile_name: Annotated[
            str, Argument(help="The [bold]name[/bold] of the [bold]profile[/bold] to view.")] = None,
        plugin_name: Annotated[str, Argument(help="The name of the plugin to add.")] = None,
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile = profile_registry.get(profile_id)

    plugin_name: str = validate_and_prompt_plugin_name(plugin_name)
    plugin: BasePlugin = plugin_registry.get(plugin_name)

    if plugin.job == PluginJob.CREATE_ORDER:
        for plugin in profile.plugins:
            if plugin.job == PluginJob.CREATE_ORDER:
                console.print(
                    f"[bold red]Error:[/bold red] Only one plugin can be of type '[bold]CREATE_ORDER[/bold]'.\n"
                    f"Remove {plugin_name} to add {plugin_name} to the profile.",
                    style="bold red",
                )
                return

    settings: dict[str, any] = create_edit_object_settings(plugin)

    console.print(Panel(create_param_table(settings),
                        title="SETTINGS",
                        border_style="bold bright_magenta",
                        expand=False))

    conformation = Prompt.ask("[bold yellow]Are you sure you want to add this Trading Component?[/bold yellow]",
                              choices=["y", "n"], default="y")

    if conformation.lower() == "n":
        return

    with Status("Adding Plugin...", spinner="dots") as status:
        plugin_instance: BasePlugin = plugin(**settings)

        if profile.add_plugin(plugin_instance):
            console.print(
                f"[bold green]Plugin '[bold]{plugin_name}[/bold]' successfully added to profile '[bold]{profile_name}[/bold]'.")
        else:
            console.print(
                f"[bold red]Error:[/bold red] Unable to add plugin '[bold]{plugin_name}[/bold]' to profile '[bold]{profile_name}[/bold]'.\n"
                f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
                style="bold red",
            )


def update_plugin_command(
        profile_name: Annotated[
            str, Argument(help="The [bold]name[/bold] of the [bold]profile[/bold] to view.")] = None,
        plugin_id: Annotated[str, Argument(help="The id of the plugin to update.")] = None,
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile = profile_registry.get(profile_id)

    plugin_id: int = validate_and_prompt_plugin_id(profile_id=profile_id, plugin_id=plugin_id)
    plugin: PluginDTO = profile.plugins[plugin_id]

    settings: dict[str, any] = create_edit_object_settings(plugin.instance, plugin.settings)

    if profile.update_plugin(id=plugin_id, name=plugin.name, settings=settings):
        console.print(
            f"[bold green]Plugin '[bold]{plugin_id}[/bold]' successfully updated in profile '[bold]{profile_name}[/bold]'.")
    else:
        console.print(
            f"[bold red]Error:[/bold red] Unable to update plugin '[bold]{plugin_id}[/bold]' in profile '[bold]{profile_name}[/bold]'.\n"
            f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
            style="bold red",
        )


def list_profile_plugins_command(
        profile_name: Annotated[
            str, Argument(help="The [bold]name[/bold] of the [bold]profile[/bold] to view.")] = None,
        plugin_id: Annotated[str, Argument(help="The id of the plugin to update.")] = None,
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)

    plugin_id: int = validate_and_prompt_plugin_id(profile_id=profile_id, plugin_id=plugin_id, allow_none=True)
    plugins: list[PluginDTO] = profile_registry.get(profile_id).plugins

    if plugin_id is None:
        plugin_table: Table = Table(show_header=True, header_style="bold blue", title="PLUGINS")
        plugin_table.add_column("ID", style="dim")
        plugin_table.add_column("NAME", style="bold magenta")

        for plugin in plugins:
            plugin_table.add_row(str(plugin.id), plugin.name)

        console.print(plugin_table)
    else:
        plugin_id: int = validate_and_prompt_plugin_id(profile_id=profile_id, plugin_id=plugin_id)
        plugin: PluginDTO = [plugin for plugin in plugins if plugin.id == plugin_id][0]

        console.print(Panel(create_param_table(plugin.settings),
                            title="SETTINGS",
                            border_style="bold bright_magenta",
                            expand=False))


def remove_plugin_command(
        profile_name: Annotated[
            str, Argument(help="The [bold]name[/bold] of the [bold]profile[/bold] to view.")] = None,
        plugin_id: Annotated[str, Argument(help="The id of the plugin to update.")] = None,
):
    profile_id: int = validate_and_prompt_profile_name(profile_name)
    profile = profile_registry.get(profile_id)

    plugin_id: int = validate_and_prompt_plugin_id(profile_id=profile_id, plugin_id=plugin_id)

    conformation = Prompt.ask("[bold yellow]Are you sure you want to remove this plugin?[/bold yellow]",
                              choices=["y", "n"], default="y")

    if conformation.lower() != "y":
        return

    if profile.remove_plugin(plugin_id=plugin_id):
        console.print(
            f"[bold green]Plugin '[bold]{plugin_id}[/bold]' successfully removed from profile '[bold]{profile_name}[/bold]'.")
    else:
        console.print(
            f"[bold red]Error:[/bold red] Unable to remove plugin '[bold]{plugin_id}[/bold]' from profile '[bold]{profile_name}[/bold]'.\n"
            f"Check the [underline bold green]'logs'[/underline bold green] for more details.",
            style="bold red",
        )
