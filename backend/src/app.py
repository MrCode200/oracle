import logging

from cst_logger import setup_logger  # type: ignore
from api import fetch_historical_data  # type: ignore
from strategies.indicators import SimpleMovingAverage, RelativeStrengthIndex  # type: ignore


def init_app():
    setup_logger(logging.DEBUG, 'logs/app.jsonl', stream_in_color=True, log_in_json=True)
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")
    return logger

logger: logging.Logger = init_app()

tickers: list[str] = ["ETH-USD", "BTC-USD", "AAPL"]
results_sma: dict[str, float] = {}
results_rsi: dict[str, float] = {}

for ticker in tickers:
    data_frame = fetch_historical_data(ticker, '3mo', "1h")

    signalSMA = SimpleMovingAverage.backtest(data_frame, short_period=9, long_period=21)
    signalRSI = RelativeStrengthIndex.backtest(data_frame, period=14, lower_band=15, upper_band=85)

    results_sma[ticker] = str(signalSMA * 100)
    results_rsi[ticker] = str(signalRSI * 100)

print(results_sma)
print(results_rsi)
