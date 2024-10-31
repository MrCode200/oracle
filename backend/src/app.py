import logging

from cst_logger import setup_logger # type: ignore
from api import fetch_market_chart  # type: ignore
from strategies import SimpleMovingAverageCrossover #type: ignore

setup_logger(logging.DEBUG, stream_in_color=True, log_in_json=True)

data = fetch_market_chart("BTC-USD", "5d")
print(data)
#MovingAverageCrossover.run(data)
