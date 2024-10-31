from typing import Iterable

from .indicatorBase import Indicator  # type: ignore


class SimpleMovingAverageCrossover(Indicator):
    @staticmethod
    def run(data: Iterable) -> float:
        pass

    @staticmethod
    def backtest(data: Iterable) -> float:
        pass