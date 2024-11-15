from dataclasses import dataclass


@dataclass
class Portfolio:
    id: int
    name: str
    description: str

    BASE_BALANCE: float
    balance: float
    coins: list  # better name as it can also have shares
    net_worth: float

    def cal_gain(self):
        return self.net_worth / self.BASE_BALANCE - 1

    @property
    def total_net_worth(self):
        ...
        # return self.balance + sum(self.coins)
