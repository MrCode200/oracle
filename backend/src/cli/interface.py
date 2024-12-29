import logging
import sys

import typer

sys.path.append('D:\\MyFolders\\Code\\Oracle\\backend')

from src.custom_logger.loggingManager import setup_logger

logger = logging.getLogger("oracle.app")
if False and not logger.handlers:
    from src.utils import load_config

    log_config = load_config("LOG_CONFIG")

    setup_logger(
        "oracle.app",
        log_config.get("level"),
        log_config.get("path"),
        log_config.get("add_stream_handler"),
        log_config.get("add_file_handler"),
        log_config.get("stream_in_color"),
        log_config.get("log_in_json"),
    )

from src.cli.commands import (change_status_command, clear_wallet_command,
                              delete_profile_command, list_trading_components_command,
                              list_profiles_command, start_app_command,
                              status_app_command, stop_app_command,
                              update_wallet_command, view_wallet_command,
                              add_trading_component_command, remove_trading_component_command, list_profile_plugins_command,
                              create_profile_command, update_profile_command,
                              add_plugin_command, list_plugins_command, remove_plugin_command, update_plugin_command,
                              list_profile_trading_component_command, update_trading_component_command)

app = typer.Typer(rich_markup_mode="rich")
app.command(name="list-tcs", help="Lists all available Trading Components.")(list_trading_components_command)
app.command(name="list-plugins", help="Logs a message.")(list_plugins_command)

profile_app = typer.Typer(help="Commands to interact with profiles.")
profile_app.command(name="delete", help="Deletes a profile.")(delete_profile_command)
profile_app.command(name="change-status", help="Changes the status of a profile.")(change_status_command)
profile_app.command(name="create", help="Creates a new profile.")(create_profile_command)
profile_app.command(name="update", help="Updates a profile.")(update_profile_command)

profile_app.command(name="list", help="Lists all available profiles.")(list_profiles_command)

wallet_app = typer.Typer(help="Commands to interact with the wallet.")
wallet_app.command(name="view", help="Shows the wallet of a profile.")(view_wallet_command)
wallet_app.command(name="update", help="Updates the wallet of a profile.")(update_wallet_command)
wallet_app.command(name="clear", help="Clears the wallet of a profile.")(clear_wallet_command)

trading_component_app = typer.Typer(help="Commands to interact with Trading Components.")
trading_component_app.command(name="add", help="Adds an Trading Components to a profile.")(add_trading_component_command)
trading_component_app.command(name="remove", help="Removes an Trading Components from a profile.")(remove_trading_component_command)
trading_component_app.command(name="list", help="Lists all Trading Components of a profile.")(list_profile_trading_component_command)
trading_component_app.command(name="update", help="Updates an Trading Components of a profile.")(update_trading_component_command)

plugin_app = typer.Typer(help="Commands to interact with plugins.")
plugin_app.command(name="add", help="Adds a plugin to a profile.")(add_plugin_command)
plugin_app.command(name="list", help="Lists all plugins of a profile.")(list_profile_plugins_command)
plugin_app.command(name="remove", help="Removes a plugin from a profile.")(remove_plugin_command)
plugin_app.command(name="update", help="Updates a plugin of a profile.")(update_plugin_command)

bot_app = typer.Typer(help="Commands to interact with the bot.", hidden=True)
bot_app.command(name="start", help="Runs the app.")(start_app_command)
bot_app.command(name="stop", help="Stops the app.")(stop_app_command)
bot_app.command(name="status", help="Checks the status of the app.")(status_app_command)

profile_app.add_typer(wallet_app, name="wallet")
profile_app.add_typer(trading_component_app, name="tc")
profile_app.add_typer(plugin_app, name="plugin")
app.add_typer(profile_app, name="profile")
app.add_typer(bot_app, name="bot")

command_list: list[str] = []

for command in app.registered_commands:
    command_list.append(command.name)
command_list.append("--help")

for command in profile_app.registered_commands:
    command_list.append("profile " + command.name)
command_list.append("profile --help")

for command in wallet_app.registered_commands:
    command_list.append("profile wallet " + command.name)
command_list.append("profile wallet --help")

for command in trading_component_app.registered_commands:
    command_list.append("profile tc " + command.name)
command_list.append("profile tc --help")

for command in plugin_app.registered_commands:
    command_list.append("profile plugin " + command.name)
command_list.append("profile plugin --help")

for command in bot_app.registered_commands:
    if not command.hidden:
        command_list.append("bot " + command.name)
command_list.append("bot --help")


# TODO: doesn't work currently as ctx is empty in repl
# @app.callback()
def log_command(ctx: typer.Context):
    logger.debug(f"Running command: {ctx.command.name}() with arguments: {ctx.params}")


def entrypoint():
    app()


if __name__ == "__main__":
    app()
