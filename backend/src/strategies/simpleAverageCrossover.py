from typing import Iterable

import backtrader as bt # type: ignore

from .indicatorBase import Indicator  # type: ignore


class SimpleMovingAverageCrossover(bt.Strategy):
    params = dict(
        pfast=10,
        pslow=30
    )

    def __init__(self):
        sma_fast = bt.ind.SMA(period=self.params.pfast)
        sma_slow = bt.ind.SMA(period=self.params.pslow)
        self.crossover = bt.ind.CrossOver(sma_fast, sma_slow)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        elif self.crossover < 0:
            self.close()