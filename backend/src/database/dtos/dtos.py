from dataclasses import dataclass

from src.utils.registry import tc_registry, plugin_registry


@dataclass
class ProfileDTO:
    id: int
    name: str
    status: int
    balance: float
    wallet: dict[str, float]
    paper_balance: float
    paper_wallet: dict[str, float]
    buy_limit: float
    sell_limit: float


@dataclass
class TradingComponentDTO:
    id: int
    profile_id: int
    name: str
    weight: float
    ticker: str
    interval: str
    settings: dict[str, any]

    def __post_init__(self):
        self.instance: 'BaseIndicator' = tc_registry.get(self.name)(**self.settings)

@dataclass
class PluginDTO:
    id: int
    profile_id: int
    name: str
    settings: dict[str, any]

    def __post_init__(self):
        self.instance: 'BasePlugin' = plugin_registry.get(self.name)(**self.settings)

@dataclass
class OrderDTO:
    id: int
    profile_id: int
    type: str
    ticker: str
    quantity: int
    price: float
    timestamp: str
