import pandas as pd

def determine_interval(interval: str) -> str:
    """
    Determines the valid interval for data processing.

    :param interval: The time interval for each data point
    :return: The valid interval for data processing. Defaults to '1m', '1h', '1d', or '1y' based on the suffix. If the interval is not supported by yfinance.
    """
    valid_intervals: list[str] = [
        "1m",
        "2m",
        "5m",
        "15m",
        "30m",
        "60m",
        "90m",
        "1h",
        "1d",
        "5d",
        "1wk",
        "1mo",
        "3mo",
    ]
    if interval in valid_intervals:
        return interval

    if interval[-1] == "o":
        return "1mo"
    elif interval[-1] == "k":
        return "1wk"
    else:
        return "1" + interval[-1]


# TODO: Fix code for compress_data
def compress_data(data_frame: pd.DataFrame, interval: str) -> pd.DataFrame:
    """
    The first three char of interval  are numbers => 00
    The fourth char of interval is unit of time =>  m:minute / h : hour
    """
    if interval == determine_interval(interval):
        return data_frame

    compress_amount: int = int(interval[:-1])
    n_interval: int = int(compress_amount)

    new_data_frame: pd.DataFrame = pd.DataFrame()

    for n in range(0, int((len(data_frame) + 1) / n_interval), n_interval):
        timestr: str = data_frame.index[n].strftime("%Y-%m-%d %X")
        idx: list = [
            pd.Timestamp(
                year=int(timestr[0:4]),
                month=int(timestr[5:7]),
                day=int(timestr[8:10]),
                hour=int(timestr[11:13]),
                minute=int(timestr[14:16]),
                second=int(timestr[17:19]),
            )
        ]

        data: dict[str, list] = {
            "Open": [data_frame.Open.iloc[n]],
            "Close": [data_frame.Close.iloc[n + n_interval - 1]],
            "High": [data_frame.High.iloc[n : n + n_interval].max()],
            "Low": [data_frame.Low.iloc[n : n + n_interval].min()],
            "Dividends": [0],
        }

        new_data_frame: pd.DataFrame = new_data_frame._append(
            pd.DataFrame(data, index=pd.Index(idx))
        )

    return new_data_frame
