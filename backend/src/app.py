import logging
from turtledemo.sorting_animate import partition

from custom_logger import setup_logger  # type: ignore
from api import fetch_historical_data  # type: ignore
from strategies.indicators import SimpleMovingAverage, RelativeStrengthIndex  # type: ignore

from perf import evolve


def init_app():
    setup_logger('oracle.app', logging.ERROR, 'logs/app.jsonl', stream_in_color=True, log_in_json=True)
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")
    return logger

logger: logging.Logger = init_app()

tickers: list[str] = ["ETH-USD"]
results_sma: dict[str, list[float]] = {}
results_rsi: dict[str, list[float]] = {}

data_frame = fetch_historical_data("ETH-USD", '1y', "1h")
print(SimpleMovingAverage.backtest(data_frame, short_period=14, long_period=50, parition_amount=1))
const_arguments: dict[str, any] = {"data_frame": data_frame, 'parition_amount': 12}
print(evolve(func=SimpleMovingAverage.backtest, func_settings=SimpleMovingAverage.EA_SETTINGS(),
             default_arguments=const_arguments,
             childs=12,
             generations=30,
             survivers=1,
             mutation_strength=0.2,
             mutation_probability=0.8))

# Ad option for starting arguments

"""for ticker in tickers:
    data_frame = fetch_historical_data(ticker, '1mo', "1d")

    signalSMA: list[float] = SimpleMovingAverage.backtest(data_frame, short_period=9, long_period=21, parition_amount=12)
    signalRSI: list[float] = RelativeStrengthIndex.backtest(data_frame, period=14, lower_band=15, upper_band=85, parition_amount=12)

    results_sma[ticker] = signalSMA
    results_rsi[ticker] = signalRSI

from functools import reduce
print("\n".join(
    f"{ticker}: [{', '.join(f'{value:.2%}' for value in total_value)}] == {reduce(lambda x, y: x * y, total_value):.2%}"
    for ticker, total_value in results_sma.items()
))

print("\n".join(
    f"{ticker}: [{', '.join(f'{value:.2%}' for value in total_value)}] == {reduce(lambda x, y: x * y, total_value):.2%}"
    for ticker, total_value in results_rsi.items()
))"""