import pandas as pd
from backend.src.api import fetch_historical_data

# Fetch historical data (assuming it returns a DataFrame)
data_frame = fetch_historical_data("BTC-USD", '6mo', "1h")


class Ichimoku:

    def run(df):
        df['Tenkan-sen'] = (df['High'].rolling(window=9).max() + df['Low'].rolling(window=9).min()) / 2
        df['Kijun-sen'] = (df['High'].rolling(window=26).max() + df['Low'].rolling(window=26).min()) / 2

        df['Senkou Span A'] = (df['Tenkan-sen'] + df['Kijun-sen']) / 2
        df['Senkou Span A'] = df['Senkou Span A'].shift(26)

        df['Senkou Span B'] = (df['High'].rolling(window=52).max() + df['Low'].rolling(window=52).min()) / 2
        df['Senkou Span B'] = df['Senkou Span B'].shift(26)

        df['Chikou Span'] = df['Close'].shift(-26)
        fr = [Ichimoku.ichimoku_signal_1(df),Ichimoku.ichimoku_signal_2(df),Ichimoku.chikou_span_signal(df),
              Ichimoku.combined_chikou_signal(df),Ichimoku.chikou_cloud_crossover(df)]
        return sum(fr)/5

    def ichimoku_signal_1(data_frame, lookback=2, recent=1):
        tenkan_lookback = data_frame['Tenkan-sen'].iloc[-lookback]
        kijun_lookback = data_frame['Kijun-sen'].iloc[-lookback]
        tenkan_recent = data_frame['Tenkan-sen'].iloc[-recent]
        kijun_recent = data_frame['Kijun-sen'].iloc[-recent]

        if tenkan_lookback > kijun_lookback and tenkan_recent < kijun_recent:

            return -1#sell
        elif tenkan_lookback < kijun_lookback and tenkan_recent > kijun_recent:

            return 1 #buy

        return 0 #hold

    def ichimoku_signal_2(data_frame, lookback=4, recent=1):

        senkou_b = data_frame["Senkou Span B"].iloc[-lookback:-recent]
        senkou_a = data_frame["Senkou Span A"].iloc[-lookback:-recent]

        close = data_frame["Close"].iloc[-lookback:-recent]
        R = []
        for n in range(0, len(senkou_b)):
            if senkou_a.iloc[n] > senkou_b.iloc[n]:  # Green
                if close.iloc[n] > senkou_a.iloc[n]:  # close price higher than kumo
                    R.append(1) #strong buy
                elif close.iloc[n] < senkou_b.iloc[n]:
                    R.append(-0.5)  # close price lower than kumo -- sell
                else:
                    R.append(0) #hold

            if senkou_a.iloc[n] < senkou_b.iloc[n]:  # RED
                if close.iloc[n] < senkou_a.iloc[n]:  # close price lower than kumo
                    R.append(-1) #strong sell
                elif close.iloc[n] > senkou_a.iloc[n]:
                    R.append(0)  # close price higher than kumo -- maybe
                else:
                    R.append(0) #hold
        print(R)
        return R[-1]

    def chikou_span_signal(df):

        if df['Chikou Span'].iloc[-27] > df['Close'].iloc[-27]:  # بالای قیمت 26 دوره گذشته
            return 0.5#buy
        elif df['Chikou Span'].iloc[-27] < df['Close'].iloc[-27]:  # پایین‌تر از قیمت 26 دوره گذشته
            return -0.5 #sell
        else:
            return 0#hold

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
            return 1#'strong buy'
        elif chikou_above_price:
            return 0.5#'weak buy'
        elif chikou_below_price and chikou_below_cloud:
            return -1#'strong sell'
        elif chikou_below_price:
            return -0.5#'weak sell'
        else:
            return 0#'hold'

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
            return 1#buy

        # بررسی تقاطع نزولی (چیکو از بالا به پایین کومو را قطع کرده باشد)
        elif (
                chikou_prev > max(senkou_a_prev, senkou_b_prev) and  # قبلاً بالای ابر کومو بوده
                chikou_now < min(senkou_a_now, senkou_b_now)  # اکنون زیر ابر کومو است
        ):
            return -1 #sell

        # در غیر این صورت، تقاطعی رخ نداده است
        return 0#'no crossover'

    def backtest(balance,df ):

        for n in range(0,3):
            cdf = df.iloc[n:54+n]
            print(cdf)
            res = Ichimoku.run(cdf)
            print(res)


print(data_frame.iloc[0:54])
ERS = Ichimoku.run(data_frame.iloc[0:54])
print(ERS)

