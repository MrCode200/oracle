import logging

from custom_logger import setup_logger  # type: ignore
from api import fetch_historical_data  # type: ignore
from strategies.indicators import SimpleMovingAverage, RelativeStrengthIndex  # type: ignore


def init_app():
    setup_logger('oracle.app', logging.DEBUG, 'logs/app.jsonl', stream_in_color=True, log_in_json=True)
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")
    return logger

logger: logging.Logger = init_app()

tickers: list[str] = ["ETH-USD"]
results_sma: dict[str, list[float]] = {}
results_rsi: dict[str, list[float]] = {}


for ticker in tickers:
    data_frame = fetch_historical_data(ticker, '3mo', "1d")

    signalSMA: list[float] = SimpleMovingAverage.backtest(data_frame, short_period=9, long_period=21, parition_amount=1)
    signalRSI: list[float] = RelativeStrengthIndex.backtest(data_frame, period=14, lower_band=25, upper_band=85, parition_amount=1)

    results_sma[ticker] = signalSMA
    results_rsi[ticker] = signalRSI

print("\n ".join([f"{ticker}: [{', '.join([f"{value:.2%}" for value in total_value])}]"
                  for ticker, total_value in results_sma.items()]))

print("\n ".join([f"{ticker}: [{', '.join([f"{value:.2%}" for value in total_value])}]"
                  for ticker, total_value in results_rsi.items()]))

