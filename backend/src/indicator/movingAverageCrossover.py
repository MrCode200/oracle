from .indicatorBase import Indicator

class MovingAverageCrossover(Indicator):
    name: str = "Moving Average Crossover"
    image: str = "image_path"

    @staticmethod
    def run(data: list[int | float]) -> float:
        pass

    @staticmethod
    def test_accuracy(data: list[int | float]) -> float:
        pass