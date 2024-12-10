import json
import logging
import sys
import time

from utils.registry import profile_registry

sys.path.append("/workspaces/oracle/backend")

from src.custom_logger.loggingManager import setup_logger

terminate_app_flag: bool = False

def init_app():
    global terminate_app_flag

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

    from src.services.indicators import simpleMovingAverageIndicator
    logger.info("All Indicators Registered Successfully...")

    init_service()

    logger.info("All Profiles Registered Successfully...")

    try:
        while not terminate_app_flag:
                time.sleep(1)

    except KeyboardInterrupt:
        for profile in profile_registry.get().values():
            profile.deactivate()

        time.sleep(5)



def terminate_app():
    global terminate_app_flag
    terminate_app_flag = True

if __name__ == "__main__":
    init_app()
