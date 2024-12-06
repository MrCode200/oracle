from dataclasses import dataclass

@dataclass
class ProfileDTO:
    id: int
    name: str
    status: int
    balance: float
    wallet: dict[str, float]
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

@dataclass
class PluginDTO:
    id: int
    profile_id: int
    name: str
    settings: dict[str, any]

@dataclass
class OrderDTO:
    id: int
    profile_id: int
    type: str
    ticker: str
    quantity: int
    price: float
    timestamp: str
