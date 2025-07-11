import pytest
from src.api.utils import determine_interval

valid_intervals: list[str] = ['1s',
                              '1m', '3m', '5m', '15m', '30m',
                              '1h', '2h', '4h', '6h', '8h', '12h',
                              '1d', '3d',
                              '1w',
                              '1M']


def test_determine_interval_valid_interval():
    for interval in valid_intervals:
        assert determine_interval(interval) == interval


@pytest.mark.parametrize("interval", ["6m", "4h", "3d", "20m"])
def test_determine_interval_invalid_short_interval(interval):
    assert determine_interval(interval) == "1" + interval[-1]


@pytest.mark.parametrize("interval", ["4mo", "4wk"])
def test_determine_interval_invalid_long_interval(interval):
    assert determine_interval(interval) == "1" + interval[-2] + interval[-1]