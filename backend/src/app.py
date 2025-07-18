import atexit
import logging
import os.path
import time
from dotenv import load_dotenv

from src.custom_logger.loggingManager import setup_logger
from src.constants import Status
from src.utils.registry import profile_registry


def init_app():
    ENV_PATH: str = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
    load_dotenv(ENV_PATH)

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

    atexit.register(stop_app)

    from src.services import init_service

    logger.info("Initializing Oracle...")

    from src.services.entities.tradingComponents import BaseTradingComponent

    logger.info("All Indicators Registered Successfully...")

    init_service()

    logger.info("All Profiles Registered Successfully...")



def stop_app():
    from src.database import engine

    logger = logging.getLogger("oracle.app")


    for profile in profile_registry.get().values():
        profile.change_status(Status.INACTIVE)

    logger.info("All Profiles Deactivated Successfully...")


    engine.dispose()
    logger.info("Database Disposed Successfully...")

    logger.info("Oracle Waiting for tasks to finish...")
    time.sleep(5)

    logger.info("Oracle Stopped Successfully!")