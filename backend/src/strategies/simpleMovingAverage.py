from typing import Iterable

from pandas import DataFrame, Series
import pandas_ta as ta

from .indicatorBase import Indicator  # type: ignore


class SimpleMovingAverage(Indicator):
    @staticmethod
    def evaluate(data_frame: DataFrame, short_period: int = 14, long_period: int = 50) -> bool | None:
        sma_short_results: Series = data_frame.ta.sma(close=data_frame[('Close', 'BTC-USD')], length=short_period)
        sma_long_results: Series = data_frame.ta.sma(close=data_frame[('Close', 'BTC-USD')], length=long_period)
        print(sma_short_results.iloc[-2], sma_long_results.iloc[-2])
        print(sma_short_results.iloc[-1], sma_long_results.iloc[-1])

        # Short crosses long from above: buy
        if sma_short_results[-1] > sma_long_results[-1]:
            pass
        # Short crosses long from below: sell
        # Short crosses long from below: sell
        return True

    @staticmethod
    def backtest(data: Iterable) -> float:
        pass