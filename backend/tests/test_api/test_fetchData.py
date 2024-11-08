import pytest
from pandas import DataFrame
from unittest.mock import patch
from backend.src.api import fetch_historical_data  # Replace with the actual module name

import logging
#logging.disable(logging.CRITICAL)

# Mock data for successful response
MOCK_DATA = DataFrame({
    'Open': [100, 102, 101],
    'High': [103, 104, 105],
    'Low': [99, 100, 100],
    'Close': [102, 103, 104],
    'Volume': [1000, 1500, 1200]
})

@pytest.mark.parametrize(
    "ticker, period, interval, start, end",
    [
        ("BTC-USD", "1d", "1d", None, None),
        ("AAPL", "1mo", "1d", "2024-01-01", "2024-01-31"),
        ("TSLA", "1y", "1h", None, None)
    ]
)

def test_fetch_successful(ticker, period, interval, start, end, caplog):
    with caplog.at_level(logging.INFO):
        result = fetch_historical_data(ticker, period, interval, start, end)
        assert isinstance(result, DataFrame)
        assert not result.empty
        assert "Open" in result.columns

        # Check if the correct info log was generated
        assert f"Fetched Data: ticker = '{ticker}'; period = '{period}'; interval = '{interval}'" in caplog.text


def test_fetch_no_data(caplog):
    with caplog.at_level(logging.ERROR):
        result = fetch_historical_data("INVALID_TICKER", "1mo", "1d")
        assert result is None
        assert "No data fetched for the given parameters." in caplog.text