import mysql.connector

from json import dumps

from utils import load_query
from utils.db_utils import prepare_connection
from sqlRunner import run_query

map = {
    "profile_name": "test_profile_2",
    "balance": 11000,
    "stop_loss": 0.01,
    "wallet": '{"SOL-USD": 100, "ETH-USD": 200}',
    "algorithm_settings": '{"MovingAverageConvergenceDivergence": {}}',
    "fetch_setting": '{"period": "1y", "interval": "1h"}',
}

kwargs2 = {
    "profile_name": "test_profile",
}

kwargs3 = {
    "profile_id": 1,
    "type": "buy",
    "ticker": "BTC",
    "quantity": 10,
    "price": 100
}

print(run_query(query_name="setup_db"))
