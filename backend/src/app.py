import logging

from cst_logger import setup_logger  # type: ignore
from api import fetch_historical_data  # type: ignore
from strategies import SimpleMovingAverage  # type: ignore


def init_app():
    setup_logger(logging.DEBUG, 'logs/app.jsonl', stream_in_color=True, log_in_json=True)
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")
    return logger

logger = init_app()

# Fetch market chart data
data_frame = fetch_historical_data("BTC-USD", '1mo', "1h")

option = SimpleMovingAverage.evaluate(data_frame)
print(option)
