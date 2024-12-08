import json
import logging
import sys

sys.path.append("/workspaces/oracle/backend")

from custom_logger.loggingManager import setup_logger


def init_app():
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
    from services import init_service

    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")

    logger.info("All Indicators Registered Successfully...")

    init_service()

if __name__ == "__main__":
    init_app()
