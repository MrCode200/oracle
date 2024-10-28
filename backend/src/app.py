import logging

from loggingManager import setup_logging
from api import fetch_market_chart
from indicator import MovingAverageCrossover

setup_logging(stream_handler_level=logging.WARNING, log_in_json=True)

data = fetch_market_chart("bitcoin", "5d")
print(data)
MovingAverageCrossover.run(data)