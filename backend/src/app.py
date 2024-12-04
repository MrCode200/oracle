import json
import logging
import sys

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

    import database  # type: ignore

    init_service()


if __name__ == "__main__":
    init_app()
