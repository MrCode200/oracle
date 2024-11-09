import logging

from cst_logger import setup_logger  # type: ignore
from api import fetch_historical_data  # type: ignore
from strategies.indicators import SimpleMovingAverage, RelativeStrengthIndex  # type: ignore


def init_app():
    setup_logger('oracle.app', logging.INFO, 'logs/app.jsonl', stream_in_color=True, log_in_json=True)
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")
    return logger

logger: logging.Logger = init_app()

tickers: list[str] = ["ETH-USD", "AAPL", "BTC-USD"]
results_sma: dict[str, list[float]] = {}
results_rsi: dict[str, list[float]] = {}


for ticker in tickers:
    data_frame = fetch_historical_data(ticker, '1y', "1h")

    signalSMA: list[float] = SimpleMovingAverage.backtest(data_frame, short_period=9, long_period=21, partition_frequency=31*24)
    signalRSI: list[float] = RelativeStrengthIndex.backtest(data_frame, period=14, lower_band=15, upper_band=85, partition_frequency=31*24)

    results_sma[ticker] = signalSMA
    results_rsi[ticker] = signalRSI

print("\n ".join([f"{ticker}: [{', '.join([f"{value:.2%}" for value in total_value])}]"
                  for ticker, total_value in results_sma.items()]))

print("\n ".join([f"{ticker}: [{', '.join([f"{value:.2%}" for value in total_value])}]"
                  for ticker, total_value in results_rsi.items()]))