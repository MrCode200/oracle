from src.api import fetch_klines
from src.app import init_app
from src.services.entities.tradingComponents import MovingAverageConvergenceDivergence, SimpleMovingAverage
import time

init_app()

if __name__ == '__main__':
    from src.utils.registry import profile_registry
    from src.services.entities import Profile
    prof: Profile = profile_registry.get(1)

    start = time.time()
    prof.evaluate()
    print(time.time() - start)
