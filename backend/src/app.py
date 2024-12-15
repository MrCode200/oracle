import logging
import time

from src.custom_logger.loggingManager import setup_logger
from src.utils.registry import profile_registry


def init_app(repl: bool = False):
    logger = logging.getLogger("oracle.app")
    if not logger.hasHandlers():
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

    from src.services import init_service

    logger.info("Initializing Oracle...")

    from src.services.indicators import simpleMovingAverageIndicator
    logger.info("All Indicators Registered Successfully...")

    init_service()

    logger.info("All Profiles Registered Successfully...")

    if repl:
        return

    # Was if I ever wanted to code cli again
    try:
        logger.info("Starting Oracle main loop...")
        while True:
            time.sleep(1)

        # read Fifo file

    finally:
        for profile in profile_registry.get().values():
            profile.deactivate()

        logger.info("All Profiles Deactivated Successfully. Closing Oracle...")

        time.sleep(5)





if __name__ == "__main__":
    from src.cli import repl
    repl()