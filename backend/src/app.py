import logging

from cst_logger import setup_logger  # type: ignore
from api import fetch_market_chart  # type: ignore
from strategies import SimpleMovingAverage  # type: ignore


def init_app():
    setup_logger(logging.DEBUG, 'logs/app.jsonl', stream_in_color=True, log_in_json=True)
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")
    return logger

logger = init_app()

# Fetch market chart data
data_frame = fetch_market_chart("BTC-USD", '1mo', "1h")

option = SimpleMovingAverage.evaluate(data_frame)
print(option)
# ------------------------------------------------------------------------------

"""import pandas as pd  # type: ignore
import pandas_ta as ta  # type: ignore


rsi_values = data_frame['SMA_14']
print(rsi_values.tail(30))  # Display the last 30 RSI values"""