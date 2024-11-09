import logging

from backend.src.api.utils.dataAnalyse import getData
from backend.src.strategies.indicators import RelativeStrengthIndex, SimpleMovingAverage
from cst_logger import setup_logger  # type: ignore
from api import fetch_historical_data  # type: ignore



def init_app():
    setup_logger(logging.INFO, 'logs/app.jsonl', stream_in_color=True, log_in_json=True)
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")
    return logger

logger = init_app()

# Fetch market chart data
data_frame = getData("AVAX-USD", '6mo', "001h") #fetch_historical_data("ADA-USD", '3mo', "1h")
if data_frame is None:
    exit(1)

signalSMA = SimpleMovingAverage.backtest(data_frame, short_period=9, long_period=21)
signalRSI = RelativeStrengthIndex.backtest(data_frame, period=14, lower_band=15, upper_band=85)

signalSMA = float(signalSMA)
signalRSI = float(signalRSI)

print(f"{signalRSI * 100 = }%, {signalSMA * 100 = }%")
