from random import randrange
from statistics import mean

from pandas import DataFrame


def create_mutation_range(funckwargs, mutation_strength) -> dict[str, int | float]:
    mutation_ranges: dict[str, int | float] = {
        key: (value["stop"] - value["start"]) * mutation_strength
        for key, value in funckwargs.items()
    }

    return mutation_ranges


def init_generation(childs: int, funckwargs: dict[str, dict[str, int | float]]) -> dict[float, dict[str, int | float]]:
    gen_statistics: dict[float, dict[str, int | float]] = []

    for child in range(childs):
        starting_args: dict[str, int | float] = {
            key: randrange(value["start"], value["stop"], value["step"])
            for key, value in funckwargs.items(),
        }

        gen_statistics[child] = starting_args
        gen_statistics[child]["total_net_worth"] = 1

    return gen_statistics

def evolve(data_frame: DataFrame,
           func: callable,
           func_settings: dict[str, dict[str, int | float]],
           childs: int = 9,
           generations: int = 10,
           survivers: int = 3,
           mutation_strength: float = 0.1) -> list[any]:
    if {"start", "end", "step"} not in func_settings.values():
        raise ValueError(f"func_settings must contain a str, dictionary where the dictionary contains the keys 'start', 'end', and 'step'")

    mutation_ranges = create_mutation_range(func_settings, mutation_strength)
    gen_statistics = init_generation(childs, func_settings)

    for gen in range(generations):
        # Sort by performance and only save the n-survivers best performers
        gen_statistics.sort()
        # remove the worst performers up to the amount of survivers
        # Add the best performers to a new dict in a loop until the number of childs is reached
        # set the gen_statistics == new dict

        # For number of survivers create
        for mother in range(survivers):
            for child in range(survivers):
                evolved_args: dict[str, int | float] = \
                {
                    key: values + randrange(-mutation_ranges[key], mutation_ranges[key], func_settings[key]["step"])
                    for key, values in gen_statistics[child].items() if key != "total_net_worth"
                }

                performance: list[float] = func(data_frame, **{key: value for key, value in evolved_args if key != "total_net_worth"})
                true_performance: float = mean(performance)

                gen_statistics[child] = evolved_args
                gen_statistics[child]["performance"] = true_performance


funckwargs: {
    "short_period": ("start": 100, "stop": 200, "step": 1),
    "long_period": ("start": 1, "stop": 100, "step": 1),
}

gen_statistics = {
    0: {
        "short_period": random,
        "long_period": random,
        "performance" : float
    },
    1: {
        "short_period": random,
        "long_period": random,
        "performance": float
    }
}