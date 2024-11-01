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

# ------------------------------------------------------------------------------

import pandas as pd  # type: ignore
import pandas_ta as ta  # type: ignore

rsi = ta.rsi(close=data_frame['Close'], length=40)

print(rsi)
