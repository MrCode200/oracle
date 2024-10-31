"""import logging

from loggingManager import setup_logging # type: ignore
from api import fetch_market_chart  # type: ignore
from strategies import MovingAverageCrossover #type: ignore

setup_logging(stream_handler_level=logging.WARNING, log_in_json=True)

data = fetch_market_chart("bitcoin", "5d")
print(data)
MovingAverageCrossover.run(data)
"""


from strategies import SimpleMovingAverageCrossover  # type: ignore
import backtrader as bt  # type: ignore
import yfinance as yf  # type: ignore


# Create a Cerebro engine instance
cerebro = bt.Cerebro()
cerebro.addstrategy(SimpleMovingAverageCrossover)
cerebro.broker.setcash(10000.0)


# Download historical data from Yahoo Finance
data = bt.feeds.PandasData(dataname=yf.download('BTC-USD', start='2020-01-01', end='2020-12-31'))
cerebro.adddata(data)


# Run and plot
cerebro.run()
cerebro.plot()