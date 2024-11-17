import logging

from custom_logger import setup_logger  # type: ignore
from api import fetch_historical_data  # type: ignore
from services.indicators import (SimpleMovingAverage,
                                 RelativeStrengthIndex,
                                 MovingAverageConvergenceDivergence,
                                 ExponentialMovingAverage)  # type: ignore

from perf import evolve


def init_app():
    setup_logger('oracle.app', logging.DEBUG, 'logs/app.jsonl', stream_in_color=True, log_in_json=True)
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")
    return logger


logger: logging.Logger = init_app()

tickers: list[str] = ["BCH-USD", "SOL-USD", "BTC-USD", "ETH-USD", "DOT-USD", "XRP-USD", "ETC-USD", "AVAX-USD"]
results_sma: dict[str, list[float]] = {}
results_rsi: dict[str, list[float]] = {}
results_macd: dict[str, list[float]] = {}
results_ema: dict[str, list[float]] = {}

"""data_frame = fetch_historical_data("BTC-USD", '1y', "3h")
const_arguments: dict[str, any] = {"data_frame": data_frame}
print(evolve(func=SimpleMovingAverage.backtest, func_settings=SimpleMovingAverage.EA_SETTINGS(),
             default_arguments=const_arguments,
             childs=12,
             generations=30,
             survivers=3,
             mutation_strength=0.1,
             mutation_probability=0.7))"""
sma = SimpleMovingAverage(short_period=9, long_period=21,
                          return_crossover_weight=False, max_crossover_gradient_degree=90,
                          crossover_gradient_signal_weight=1, crossover_weight_impact=0.2001)
rsi = RelativeStrengthIndex(period=14, lower_band=15, upper_band=85)
ema = ExponentialMovingAverage(period=50)
macd = MovingAverageConvergenceDivergence(fast_period=12, slow_period=26,
                                          signal_line_period=9,
                                          max_momentum_lookback=100,
                                          momentum_signal_weight=0.6,
                                          return_crossover_weight=False,
                                          max_crossover_gradient_degree=80,
                                          crossover_gradient_signal_weight=1,
                                          crossover_weight_impact=0.7,
                                          zero_line_crossover_weight=1,
                                          zero_line_pullback_lookback=100,
                                          zero_line_pullback_tolerance_percent=0.01,
                                          zero_line_pullback_weight=0.0,
                                          return_pullback_strength=True,
                                          rate_of_change_weight=1, magnitude_weight=1,
                                          weight_impact=0.25)

for ticker in tickers:
    df = fetch_historical_data(ticker, '1y', "1h")

    signalSMA: list[float] = sma.backtest(df=df, partition_amount=12)
    signalRSI: list[float] = [0]  # rsi.backtest(df=df, partition_amount=12)
    signalEMA: list[float] = [0]  # ema.backtest(df=df, partition_amount=12)
    signalMACD: list[float] = [0] # macd.backtest(df=df, partition_amount=12)

    results_sma[ticker] = signalSMA
    results_rsi[ticker] = signalRSI
    results_macd[ticker] = signalMACD
    results_ema[ticker] = signalEMA

from functools import reduce

print("EMA:")
print("\n".join(
    f"{ticker}: [{', '.join(f'{value:.2%}' for value in total_value)}] == {reduce(lambda x, y: x * y, total_value):.2%}"
    for ticker, total_value in results_ema.items()
))
print("MACD:")
print("\n".join(
    f"{ticker}: [{', '.join(f'{value:.2%}' for value in total_value)}] == {reduce(lambda x, y: x * y, total_value):.2%}"
    for ticker, total_value in results_macd.items()
))
print("SMA:")
print("\n".join(
    f"{ticker}: [{', '.join(f'{value:.2%}' for value in total_value)}] == {reduce(lambda x, y: x * y, total_value):.2%}"
    for ticker, total_value in results_sma.items()
))
print("RSI:")
print("\n".join(
    f"{ticker}: [{', '.join(f'{value:.2%}' for value in total_value)}] == {reduce(lambda x, y: x * y, total_value):.2%}"
    for ticker, total_value in results_rsi.items()
))
