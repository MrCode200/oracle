from src.api import fetch_klines
from src.app import init_app
from src.services.entities.tradingComponents import MovingAverageConvergenceDivergence, SimpleMovingAverage

init_app()

if __name__ == '__main__':
    from src.utils.registry import profile_registry
    from src.services.entities import Profile

    prof: Profile = profile_registry.get(1)
    # result = prof.backtest(1_000_000, 7, 7)

    df = fetch_klines(ticker="BTCUSDT", interval="1h", days=7)
    result2 = prof.trading_components[0].instance.evaluate(df=df)
    sma = SimpleMovingAverage(short_period=14, long_period=50, return_crossover_weight=True)
    macd = MovingAverageConvergenceDivergence(slow_period=26, fast_period=12, signal_line_period=9, weight_impact=0)
    result = macd.evaluate(df=df)
    print(result)
    print(result2)