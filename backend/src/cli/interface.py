import logging

import typer

from src.custom_logger.loggingManager import setup_logger

logger = logging.getLogger("oracle.app")

app = typer.Typer()

from src.cli.commands import crud_profile_app

app.add_typer(crud_profile_app, name="profile")

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


def main():
    app()
