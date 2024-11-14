import pandas as pd
from backend.src.api import fetch_historical_data

# Fetch historical data (assuming it returns a DataFrame)
data_frame = fetch_historical_data("ETH-USD", '1mo', "1h")

class Ichimoku:

    def run(df):
        df['Tenkan-sen'] = (df['High'].rolling(window=9).max() + df['Low'].rolling(window=9).min()) / 2
        df['Kijun-sen'] = (df['High'].rolling(window=26).max() + df['Low'].rolling(window=26).min()) / 2


        df['Senkou Span A'] = (df['Tenkan-sen'] + df['Kijun-sen']) / 2
        df['Senkou Span A'] = df['Senkou Span A'].shift(26)

        df['Senkou Span B'] = (df['High'].rolling(window=52).max() + df['Low'].rolling(window=52).min()) / 2
        df['Senkou Span B'] = df['Senkou Span B'].shift(26)

        df['Chikou Span'] = df['Close'].shift(-26)


        return df[['High', 'Low', 'Tenkan-sen', 'Kijun-sen', 'Senkou Span A']]

    def ichimoku_signal(data_frame, lookback=9, recent=7):
        tenkan_lookback = data_frame['Tenkan-sen'].iloc[-lookback]
        kijun_lookback = data_frame['Kijun-sen'].iloc[-lookback]
        tenkan_recent = data_frame['Tenkan-sen'].iloc[-recent]
        kijun_recent = data_frame['Kijun-sen'].iloc[-recent]

        if tenkan_lookback > kijun_lookback and tenkan_recent < kijun_recent:
            print(tenkan_lookback ," ", kijun_lookback,"   ",tenkan_recent, " " ,kijun_recent)
            return 'sell'
        elif tenkan_lookback < kijun_lookback and tenkan_recent > kijun_recent:
            print(tenkan_lookback, " ", kijun_lookback, "   ", tenkan_recent, " ", kijun_recent)
            return 'buy'
        print(tenkan_lookback, " ", kijun_lookback, "   ", tenkan_recent, " ", kijun_recent)
        return 'hold'

df1 = Ichimoku.run(data_frame)
res = Ichimoku.ichimoku_signal(df1)
print(res)












