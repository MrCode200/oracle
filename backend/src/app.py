import logging

from cst_logger import setup_logger  # type: ignore
from api import fetch_historical_data  # type: ignore
from strategies import SimpleMovingAverage, RelativeStrengthIndex  # type: ignore


def init_app():
    setup_logger(logging.DEBUG, 'logs/app.jsonl', stream_in_color=True, log_in_json=True)
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")
    return logger

logger = init_app()

# Fetch market chart data
data_frame = fetch_historical_data("XRP-USD", '1mo', "1h")
if data_frame is None:
    exit(1)

signalSMA = SimpleMovingAverage.backtest(data_frame, short_period=5, long_period=20)
signalRSI = SimpleMovingAverage.backtest(data_frame, short_period=14, long_period=50)
print(f"{signalRSI = }, {signalSMA = }")

#signalRSI = np.float64(1.238658743286133), signalSMA = np.float64(1.015741122619629)
