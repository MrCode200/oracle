from dataclasses import dataclass

from backend.src.services.indicators import BaseIndicator
from backend.src.services.plugin import BasePlugin
from backend.src.utils.registry import indicator_registry, plugin_registry


@dataclass
class ProfileDTO:
    id: int
    name: str
    status: int
    balance: float
    wallet: dict[str, float]
    paper_balance: float
    paper_wallet: dict[str, float]
    strategy_settings: dict[str, any]

@dataclass
class IndicatorDTO:
    id: int
    profile_id: int
    name: str
    weight: float
    ticker: str
    interval: str
    settings: dict[str, any]

    def __post_init__(self):
        self.instance: BaseIndicator = indicator_registry.get(self.name)(**self.settings)

@dataclass
class PluginDTO:
    id: int
    profile_id: int
    name: str
    settings: dict[str, any]

    def __post_init__(self):
        self.instance: BasePlugin = plugin_registry.get(self.name)(**self.settings)

@dataclass
class OrderDTO:
    id: int
    profile_id: int
    type: str
    ticker: str
    quantity: int
    price: float
    timestamp: str
