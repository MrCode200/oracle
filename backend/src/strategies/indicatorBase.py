from abc import ABC, abstractmethod
from typing import Iterable


class Indicator(ABC):
    """
    Defines an abstract base class for indicators.

    Methods
        - run(database: Iterable) -> float: Abstract method to run the strategies on the provided database.
        - test_accuracy(database: Iterable) -> float: Abstract method to test the accuracy of the strategies on the provided database.
    """
    @staticmethod
    @abstractmethod
    def evaluate(data: Iterable) -> bool:
        ...

    @staticmethod
    @abstractmethod
    def backtest(data: Iterable) -> float:
        ...