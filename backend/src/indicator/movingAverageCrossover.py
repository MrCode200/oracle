from typing import Iterable

from .indicatorBase import Indicator


class MovingAverageCrossover(Indicator):
    @staticmethod
    def run(data: Iterable[int | float]) -> float:
        pass

    @staticmethod
    def test_accuracy(data: Iterable[int | float]) -> float:
        pass
