import mysql.connector

from utils import load_query
from utils.db_utils import prepare_connection
from sqlRunner import run_query

kwargs = {
    "profile_name": "test_profile",
    "balance": 1000,
    "stop_loss": 0.01,
    "wallet": '{"coinA": 100, "coinB": 200}',
    "algorithms": '{"test_algorithms": {"arg1": "value1", "arg2": "value2"}}',
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

print(run_query("setup_db", **kwargs2))
