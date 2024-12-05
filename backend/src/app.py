import json
import logging
import sys

from backend.src.services.cli import init_cli

sys.path.append("/workspaces/oracle/backend")

from custom_logger.loggingManager import setup_logger  # type: ignore
from services import init_service  # type: ignore


def init_app():
    with open("backend/config/config.json", "r") as f:
        log_config = json.load(f).get("LOG_CONFIG")

    setup_logger(
        "oracle.app",
        log_config.get("level"),
        log_config.get("path"),
        log_config.get("stream_in_color"),
        log_config.get("log_in_json"),
    )
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")

    import backend.src.services.indicators as indicators
    logger.info("All Indicators Registered Successfully...")

    init_service()

    init_cli()


if __name__ == "__main__":
    init_app()
