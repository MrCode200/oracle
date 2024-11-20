import logging

from custom_logger import setup_logger  # type: ignore
from services import init_service
from api import fetch_historical_data  # type: ignore

algo_blacklist: list[str] = ["ichimoku"]


def init_app():
    setup_logger('oracle.app', logging.DEBUG, '../../logs/app.jsonl', stream_in_color=True, log_in_json=True)
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")

    # register all models
    import algorithms.indicators as indicators
    sma = indicators.SimpleMovingAverage()

    init_service()
    return logger

init_app()
# -----
from services.utils import yield_profiles

while True:
    command = input("Command: ")
    if command == "evaluate" or command == "eval":
        for profile in yield_profiles():
            print(f"Profile: {profile.profile_name}")
            print(profile.evaluate())
