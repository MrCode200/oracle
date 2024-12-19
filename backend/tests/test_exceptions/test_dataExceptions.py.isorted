import pytest
from src.exceptions import DataFetchError


def test_data_fetch_error():
    try:
        raise DataFetchError(ticker="BTC-USD", period="1d", start="2022-01-01", end="2022-01-31")
    except DataFetchError as e:
        assert str(
            e) == "Error occurred while Fetching data.\nArguments passed: {'ticker': 'BTC-USD', 'period': '1d', 'start': '2022-01-01', 'end': '2022-01-31'}"


def test_data_fetch_error_with_custom_message():
    ticker = "BTC-USD"
    try:
        raise DataFetchError(message=f"Custom message.", ticker=ticker)
    except DataFetchError as e:
        assert str(e) == "Custom message.\nArguments passed: {'ticker': 'BTC-USD'}"
