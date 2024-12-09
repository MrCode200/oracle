import logging

import typer

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

from src.cli.commands import delete_profile, activate_profile, deactivate_profile, command_list_indicators, command_list_profiles, start_app, stop_app

app = typer.Typer()
app.command(name="list-indicators",help="Lists all available indicators.")(command_list_indicators)
app.command(name="list-profiles", help="Lists all available profiles.")(command_list_profiles)

crud_profile_app = typer.Typer()
crud_profile_app.command(name="delete", help="Deletes a profile.")(delete_profile)
crud_profile_app.command(name="activate", help="Activates a profile.")(activate_profile)
crud_profile_app.command(name="deactivate", help="Deactivates a profile.")(deactivate_profile)

bot_app = typer.Typer()
bot_app.command(name="start", help="Runs the app.")(start_app)
bot_app.command(name="stop", help="Stops the app.")(stop_app)

app.add_typer(crud_profile_app, name="profile")
app.add_typer(bot_app, name="bot")


def main():
    app()
