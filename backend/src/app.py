import logging

from custom_logger import setup_logger  # type: ignore
from api import fetch_historical_data  # type: ignore
from strategies.indicators import SimpleMovingAverage, RelativeStrengthIndex  # type: ignore

from perf import evolve


def init_app():
    setup_logger('oracle.app', logging.ERROR, 'logs/app.jsonl', stream_in_color=True, log_in_json=True)
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")
    return logger
2.3179159427338805
logger: logging.Logger = init_app()

tickers: list[str] = ["ETH-USD"]
results_sma: dict[str, list[float]] = {}
results_rsi: dict[str, list[float]] = {}

data_frame = fetch_historical_data("BTC-USD", '1y', "1h")
const_arguments: dict[str, any] = {"data_frame": data_frame}
print(evolve(func=RelativeStrengthIndex.backtest, func_settings=RelativeStrengthIndex.EA_SETTINGS(),
             default_arguments=const_arguments,
             childs=12,
             generations=30,
             survivers=3,
             mutation_strength=0.05,
             mutation_probability=0.5))

"""for ticker in tickers:
    data_frame = fetch_historical_data(ticker, '3mo', "1d")

    signalSMA: list[float] = SimpleMovingAverage.backtest(data_frame, short_period=9, long_period=21, parition_amount=1)
    signalRSI: list[float] = RelativeStrengthIndex.backtest(data_frame, period=14, lower_band=25, upper_band=85, parition_amount=1)

    results_sma[ticker] = signalSMA
    results_rsi[ticker] = signalRSI

print("\n ".join([f"{ticker}: [{', '.join([f"{value:.2%}" for value in total_value])}]"
                  for ticker, total_value in results_sma.items()]))

print("\n ".join([f"{ticker}: [{', '.join([f"{value:.2%}" for value in total_value])}]"
                  for ticker, total_value in results_rsi.items()]))"""

