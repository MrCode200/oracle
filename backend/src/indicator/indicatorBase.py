from abc import abstractmethod


class Indicator:
    @classmethod
    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, 'name') or not hasattr(cls, 'image'):
            raise AttributeError(f"{cls.__name__} must have the attributes 'name' and 'image' defined")

    @abstractmethod
    @staticmethod
    def run(data):
        ...

    @abstractmethod
    @staticmethod
    def test_accuracy(data):
        ...