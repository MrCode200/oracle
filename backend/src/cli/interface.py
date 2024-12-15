import logging
import sys

import typer

sys.path.append('D:\\MyFolders\\Code\\Oracle\\backend')

from src.cli.commands.profileCommands.crudProfileCommands import \
    command_create_profile
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

from src.cli.commands import (command_activate_profile,
                              command_deactivate_profile,
                              command_delete_profile, command_list_indicators,
                              command_list_profiles, command_start_app,
                              command_status_app, command_stop_app,
                              command_update_wallet, command_view_wallet,
                              command_clear_wallet)

app = typer.Typer(rich_markup_mode="rich")
app.command(name="list-indicators", help="Lists all available indicators.")(command_list_indicators)

profile_app = typer.Typer(help="Commands to interact with profiles.")
profile_app.command(name="delete", help="Deletes a profile.")(command_delete_profile)
profile_app.command(name="activate", help="Activates a profile.")(command_activate_profile)
profile_app.command(name="deactivate", help="Deactivates a profile.")(command_deactivate_profile)
profile_app.command(name="create", help="Creates a new profile.")(command_create_profile)

profile_app.command(name="list", help="Lists all available profiles.")(command_list_profiles)

wallet_app = typer.Typer(help="Commands to interact with the wallet.")
wallet_app.command(name="view", help="Shows the wallet of a profile.")(command_view_wallet)
wallet_app.command(name="update", help="Updates the wallet of a profile.")(command_update_wallet)
wallet_app.command(name="clear", help="Clears the wallet of a profile.")(command_clear_wallet)

bot_app = typer.Typer(help="Commands to interact with the bot.", hidden=True)
bot_app.command(name="start", help="Runs the app.")(command_start_app)
bot_app.command(name="stop", help="Stops the app.")(command_stop_app)
bot_app.command(name="status", help="Checks the status of the app.")(command_status_app)

profile_app.add_typer(wallet_app, name="wallet")
app.add_typer(profile_app, name="profile")
app.add_typer(bot_app, name="bot")

# TODO: doesn't work currently as ctx is empty in repl
# @app.callback()
def log_command(
    ctx: typer.Context,
):
    print(ctx.params)
    print(ctx.command.name)
    logger.debug(f"Running command: {ctx.command.name}() with arguments: {ctx.params}")

def entrypoint():
    app()

if __name__ == "__main__":
    app()