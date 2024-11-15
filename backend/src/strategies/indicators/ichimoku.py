import pandas as pd
from backend.src.api import fetch_historical_data

# Fetch historical data (assuming it returns a DataFrame)
data_frame = fetch_historical_data("BTC-USD", '1mo', "1h")


class Ichimoku:

    def run(df):
        df['Tenkan-sen'] = (df['High'].rolling(window=9).max() + df['Low'].rolling(window=9).min()) / 2
        df['Kijun-sen'] = (df['High'].rolling(window=26).max() + df['Low'].rolling(window=26).min()) / 2

        df['Senkou Span A'] = (df['Tenkan-sen'] + df['Kijun-sen']) / 2
        df['Senkou Span A'] = df['Senkou Span A'].shift(26)

        df['Senkou Span B'] = (df['High'].rolling(window=52).max() + df['Low'].rolling(window=52).min()) / 2
        df['Senkou Span B'] = df['Senkou Span B'].shift(26)

        df['Chikou Span'] = df['Close'].shift(-26)

        return df[["Close", 'High', 'Low', 'Tenkan-sen', 'Kijun-sen', 'Senkou Span A', 'Senkou Span B', 'Chikou Span']]

    def ichimoku_signal_1(data_frame, lookback=9, recent=7):
        tenkan_lookback = data_frame['Tenkan-sen'].iloc[-lookback]
        kijun_lookback = data_frame['Kijun-sen'].iloc[-lookback]
        tenkan_recent = data_frame['Tenkan-sen'].iloc[-recent]
        kijun_recent = data_frame['Kijun-sen'].iloc[-recent]

        if tenkan_lookback > kijun_lookback and tenkan_recent < kijun_recent:
            print(tenkan_lookback, " ", kijun_lookback, "   ", tenkan_recent, " ", kijun_recent)
            return 'sell'
        elif tenkan_lookback < kijun_lookback and tenkan_recent > kijun_recent:
            print(tenkan_lookback, " ", kijun_lookback, "   ", tenkan_recent, " ", kijun_recent)
            return 'buy'
        print(tenkan_lookback, " ", kijun_lookback, "   ", tenkan_recent, " ", kijun_recent)
        return 'hold'

    def ichimoku_signal_2(data_frame, lookback=90, recent=70):

        senkou_b = data_frame["Senkou Span B"].iloc[-lookback:-recent]
        senkou_a = data_frame["Senkou Span A"].iloc[-lookback:-recent]

        close = data_frame["Close"].iloc[-lookback:-recent]
        R = []
        for n in range(0, len(senkou_b)):
            if senkou_a.iloc[n] > senkou_b.iloc[n]:  # Green
                if close.iloc[n] > senkou_a.iloc[n]:  # close price higher than kumo
                    R.append("strong buy ")
                elif close.iloc[n] < senkou_b.iloc[n]:
                    R.append("sell G")  # close price lower than kumo
                else:
                    R.append("n")

            if senkou_a.iloc[n] < senkou_b.iloc[n]:  # RED
                if close.iloc[n] < senkou_a.iloc[n]:  # close price lower than kumo
                    R.append("sell R ")
                elif close.iloc[n] > senkou_a.iloc[n]:
                    R.append("maybe")  # close price higher than kumo
                else:
                    R.append("n")
        return R

    def chikou_span_signal(df):

        if df['Chikou Span'].iloc[-27] > df['Close'].iloc[-27]:  # بالای قیمت 26 دوره گذشته
            return 'buy'
        elif df['Chikou Span'].iloc[-27] < df['Close'].iloc[-27]:  # پایین‌تر از قیمت 26 دوره گذشته
            return 'sell'
        else:
            return f'hold  {df['Chikou Span'].iloc[-27]} , {df['Close'].iloc[-27]}'

    def combined_chikou_signal(df):

        # موقعیت چیکو اسپن
        chikou_above_price = df['Chikou Span'].iloc[-27] > df['Close'].iloc[-27]
        chikou_above_cloud = (
                df['Chikou Span'].iloc[-27] > df['Senkou Span A'].iloc[-27] and
                df['Chikou Span'].iloc[-27] > df['Senkou Span B'].iloc[-27]
        )
        chikou_below_price = df['Chikou Span'].iloc[-27] < df['Close'].iloc[-27]
        chikou_below_cloud = (
                df['Chikou Span'].iloc[-27] < df['Senkou Span A'].iloc[-27] and
                df['Chikou Span'].iloc[-27] < df['Senkou Span B'].iloc[-27]
        )

        # سیگنال‌های ترکیبی
        if chikou_above_price and chikou_above_cloud:
            return 'strong buy'
        elif chikou_above_price:
            return 'weak buy'
        elif chikou_below_price and chikou_below_cloud:
            return 'strong sell'
        elif chikou_below_price:
            return 'weak sell'
        else:
            return 'hold'

    def chikou_cloud_crossover(df):
        """
        بررسی تقاطع چیکو اسپن و ابر کومو
        :param df: DataFrame شامل خطوط ایچیموکو
        :return: سیگنال ('bullish crossover', 'bearish crossover', 'no crossover')
        """
        # موقعیت چیکو اسپن در دوره فعلی و دوره قبلی نسبت به Senkou Span A و Senkou Span B
        chikou_now = df['Chikou Span'].iloc[-27]
        chikou_prev = df['Chikou Span'].iloc[-28]
        senkou_a_now = df['Senkou Span A'].iloc[-27]
        senkou_b_now = df['Senkou Span B'].iloc[-27]
        senkou_a_prev = df['Senkou Span A'].iloc[-28]
        senkou_b_prev = df['Senkou Span B'].iloc[-28]

        # بررسی تقاطع صعودی (چیکو از پایین به بالا کومو را قطع کرده باشد)
        if (
                chikou_prev < min(senkou_a_prev, senkou_b_prev) and  # قبلاً زیر ابر کومو بوده
                chikou_now > max(senkou_a_now, senkou_b_now)  # اکنون بالای ابر کومو است
        ):
            return 'bullish crossover'

        # بررسی تقاطع نزولی (چیکو از بالا به پایین کومو را قطع کرده باشد)
        elif (
                chikou_prev > max(senkou_a_prev, senkou_b_prev) and  # قبلاً بالای ابر کومو بوده
                chikou_now < min(senkou_a_now, senkou_b_now)  # اکنون زیر ابر کومو است
        ):
            return 'bearish crossover'

        # در غیر این صورت، تقاطعی رخ نداده است
        return 'no crossover'


df1 = Ichimoku.run(data_frame)
res = Ichimoku.chikou_cloud_crossover(df1)
print(res)
