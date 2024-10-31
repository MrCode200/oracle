import logging

from cst_logger import setup_logger  # type: ignore
from api import fetch_market_chart  # type: ignore
from strategies import SimpleMovingAverageCrossover  # type: ignore


def init_app():
    setup_logger(logging.DEBUG, stream_in_color=True, log_in_json=True)
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")
    return logger

logger = init_app()

# Fetch market chart data
data = fetch_market_chart("BTC-USD", '1mo', "1d")

# ------------------------------------------------------------------------------
# Here i dont understand code but it seems to work, you can start writing your own or use this and understand it
# Good luck :)

import pandas as pd  # type: ignore
import pandas_ta as ta  # type: ignore

def analyze_market(data, ticker="BTC-USD", days='1mo', interval='1d', sma_length=14):
    # Print the raw data
    print("Raw Data Fetched:")
    print(data)

    # Calculate SMA
    data[('SMA', '')] = ta.sma(data[('Close', 'BTC-USD')], length=sma_length)
    data = data.dropna(subset=[('SMA', '')])

    # Extract latest values
    last_close = data[('Close', 'BTC-USD')].iloc[-1]
    previous_close = data[('Close', 'BTC-USD')].iloc[-2]
    last_sma = data[('SMA', '')].iloc[-1]
    previous_sma = data[('SMA', '')].iloc[-2]

    # Determine Buy/Sell signal
    signal = (
        "Buy" if last_close > last_sma and previous_close <= previous_sma else
        "Sell" if last_close < last_sma and previous_close >= previous_sma else
        "Hold"
    )

    # Output results
    print(data[[('Close', 'BTC-USD'), ('SMA', '')]].tail())
    print(f"Suggested Action: {signal}")

# Call the function
analyze_market(data)
