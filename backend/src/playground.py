from src.app import init_app
from multiprocessing import Process
init_app()

if __name__ == '__main__':
    from src.utils.registry import profile_registry
    from src.services.entities import Profile

    prof: Profile = profile_registry.get(1)
    process = Process(target=prof.backtest, args=(1_000_000, 7, 1))
    result = process.start()
    process.join()
    print(result)
