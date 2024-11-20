from typing import Type
from logging import getLogger

from dataclasses import dataclass, field

from pandas import DataFrame

from backend.src.algorithms.baseModel import BaseModel
from backend.src.algorithms.utils import get_model
from backend.src.api import fetch_historical_data

logger = getLogger("oracle.app")


@dataclass
class Profile:
    profile_id: int
    profile_name: str
    balance: float
    wallet: dict[str, float]
    stop_loss: float
    algorithms_settings: dict[str, dict[str, any]] = field(default_factory=list)
    algorithms: dict[str, Type[BaseModel]] = field(default_factory=dict)
    fetch_settings: dict[str, any] = field(default_factory=dict)

    def __post_init__(self):
        for model, settings in self.algorithms_settings.items():
            self.algorithms[model] = get_model(model)(**settings)

    def evaluate(self):
        results: dict[str, float] = {}
        for ticker in self.wallet:
            df: DataFrame = fetch_historical_data(ticker=ticker, **self.fetch_settings)
            for algo in self.algorithms.values():
                results[ticker] = algo.evaluate(df)

        return results

    def schedule(self):
        ...
