from logging import getLogger

from pandas import DataFrame, Series

from .indicatorBase import Indicator

logger = getLogger("oracle.app")

class ExponentialMovingAverage(Indicator):
    @staticmethod
    def evaluate(data_frame: DataFrame) -> float | int | None:
        pass

    @staticmethod
    def backtest(data_frame: DataFrame, partition_amount: int = 1) -> list[float]:
        pass