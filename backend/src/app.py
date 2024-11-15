import logging
from turtledemo.sorting_animate import partition

from custom_logger import setup_logger  # type: ignore
from api import fetch_historical_data  # type: ignore
from strategies.indicators import SimpleMovingAverage, RelativeStrengthIndex,MovingAverageConvergenceDivergence  # type: ignore

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
results_macd: dict[str, list[float]] = {}

"""data_frame = fetch_historical_data("BTC-USD", '1y', "3h")
const_arguments: dict[str, any] = {"data_frame": data_frame}
print(evolve(func=SimpleMovingAverage.backtest, func_settings=SimpleMovingAverage.EA_SETTINGS(),
             default_arguments=const_arguments,
             childs=12,
             generations=30,
             survivers=3,
             mutation_strength=0.1,
             mutation_probability=0.7))"""

for ticker in tickers:
    df = fetch_historical_data(ticker, '1y', "1h")

    signalSMA: list[float] = SimpleMovingAverage.backtest(df=df, short_period=9, long_period=21, partition_amount=12)
    signalRSI: list[float] = RelativeStrengthIndex.backtest(df=df, period=14, lower_band=15, upper_band=85, partition_amount=12)
    signalMACD: list[float] = MovingAverageConvergenceDivergence.backtest(df=df)

    results_sma[ticker] = signalSMA
    results_rsi[ticker] = signalRSI
    results_macd[ticker] =signalMACD

from functools import reduce
print("\n".join(
    f"{ticker}: [{', '.join(f'{value:.2%}' for value in total_value)}] == {reduce(lambda x, y: x * y, total_value):.2%}"
    for ticker, total_value in results_sma.items()
))
print("\n".join(
    f"{ticker}: [{', '.join(f'{value:.2%}' for value in total_value)}] == {reduce(lambda x, y: x * y, total_value):.2%}"
    for ticker, total_value in results_macd.items()
))
print("\n".join(
    f"{ticker}: [{', '.join(f'{value:.2%}' for value in total_value)}] == {reduce(lambda x, y: x * y, total_value):.2%}"
    for ticker, total_value in results_rsi.items()
))

