import logging
import sys

import typer

from src.cli.commands.profileCommands import command_view_wallet, command_update_wallet, command_clear_wallet

sys.path.append('D:\\MyFolders\\Code\\Oracle\\backend')

from src.cli.commands.profileCommands.crudProfileCommands import \
    command_create_profile
from src.custom_logger.loggingManager import setup_logger

logger = logging.getLogger("oracle.app")
if not logger.handlers:
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
                              command_status_app, command_stop_app)

app = typer.Typer(rich_markup_mode="rich")
app.command(name="list-indicators", help="Lists all available indicators.")(command_list_indicators)
app.command(name="list-profiles", help="Lists all available profiles.")(command_list_profiles)

crud_profile_app = typer.Typer(help="Commands to interact with profiles.")
crud_profile_app.command(name="delete", help="Deletes a profile.")(command_delete_profile)
crud_profile_app.command(name="activate", help="Activates a profile.")(command_activate_profile)
crud_profile_app.command(name="deactivate", help="Deactivates a profile.")(command_deactivate_profile)
crud_profile_app.command(name="create", help="Creates a new profile.")(command_create_profile)

crud_profile_app.command(name="view-wallet", help="Shows the wallet of a profile.")(command_view_wallet)
crud_profile_app.command(name="update-wallet", help="Updates the wallet of a profile.")(command_update_wallet)
crud_profile_app.command(name="clear-wallet", help="Clears the wallet of a profile.")(command_clear_wallet)

bot_app = typer.Typer(help="Commands to interact with the bot.")
bot_app.command(name="start", help="Runs the app.")(command_start_app)
bot_app.command(name="stop", help="Stops the app.")(command_stop_app)
bot_app.command(name="status", help="Checks the status of the app.")(command_status_app)

app.add_typer(crud_profile_app, name="profile")
app.add_typer(bot_app, name="bot")

#-------------
@app.command(name="t")
def test():
    pass
#------------


def entrypoint():
    app()

if __name__ == '__main__':
    entrypoint()