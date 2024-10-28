from abc import ABC, abstractmethod
from typing import Iterable


class Indicator(ABC):
    """
    Defines an abstract base class for indicators.

    Methods:
        - run(data: Iterable) -> float: Abstract method to run the indicator on the provided data.
        - test_accuracy(data: Iterable) -> float: Abstract method to test the accuracy of the indicator on the provided data.
    """
    @staticmethod
    @abstractmethod
    def run(data: Iterable) -> float:
        ...

    @staticmethod
    @abstractmethod
    def test_accuracy(data: Iterable) -> float:
        ...