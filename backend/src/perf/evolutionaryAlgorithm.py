from random import randrange
from statistics import mean
import logging


from pandas import DataFrame

logger: logging.Logger = logging.getLogger("oracle.app")

def evolve(data_frame: DataFrame,
           func: callable,
           func_settings: dict[str, dict[str, int | float]],
           childs: int = 9,
           generations: int = 10,
           survivers: int = 3,
           mutation_strength: float = 0.1) -> list[any]:
    """
    Evolves the optimal arguments for a given indicator function over multiple generations using a genetic algorithm approach.

    This function uses a genetic algorithm to optimize the arguments of a specified indicator function (`func`)
    applied to a financial dataset (`data_frame`). The optimization process aims to find the best-performing set of arguments
    that maximize the function's performance on the given dataset.

    The function initializes a population of individuals (each with a set of randomly generated arguments) and iteratively evolves them over several generations.
    In each generation, a subset of the best-performing individuals (survivors) are selected, and their arguments are mutated to produce offspring.
    The performance of each set of arguments is evaluated using the provided indicator function, and the process repeats for the specified number of generations.

    :param data_frame: A Pandas DataFrame containing the financial data used as input for the indicator function.

    :param func: The indicator function to optimize. This function should accept keyword arguments corresponding to the argument names in `func_settings`
    and return a list of performance metrics (e.g., returns or profit/loss values).

    :param func_settings: A dictionary that defines the range and step size for each argument used in the indicator function.
        Each key is the name of the argument, and the corresponding value is a dictionary with the following structure:

        .. code-block:: python

            {
                "arg_name": {"start": int, "end": int, "step": int}
            }

    :param childs: The total number of offspring to generate in each generation. Must be a multiple of `survivers`.
        Default is 9.

    :param generations: The number of generations to evolve the population. Default is 10.

    :param survivers: The number of top-performing individuals to select as parents for the next generation.
        These individuals will be used to produce new offspring. Default is 3.

    :param mutation_strength: The factor that determines the extent of mutation applied to the arguments during the evolution process.
        A higher value leads to more significant mutations. Default is 0.1 (i.e., 10% of the range).

    :raises ValueError: If `func_settings` does not contain the required keys ("start", "end", "step") for each argument,
        or if `childs` is not a multiple of `survivers`.

    :return: A list containing the best set of arguments found across all generations along with their performance score.

    :example:

        .. code-block:: python

            import pandas as pd

            # Example usage
            data = pd.read_csv('financial_data.csv')
            settings = {
                "short_period": {"start": 5, "end": 15, "step": 1},
                "long_period": {"start": 20, "end": 50, "step": 5}
            }

            best_args = evolve(
                data_frame=data,
                func=relative_strength_index,
                func_settings=settings,
                childs=10,
                generations=5,
                survivers=2
            )
            print(best_args)

    This function is useful for optimizing financial trading strategies by tuning the parameters of technical indicators
    like moving averages, RSI, or custom indicators to maximize profitability or accuracy.
    """
    if {"start", "end", "step"} not in func_settings.values():
        raise ValueError(f"func_settings must contain a str, dictionary where the dictionary contains the keys 'start', 'end', and 'step'")
    if childs % survivers != 0:
        raise ValueError("Childs must be a multiple of survivers")

    mutation_ranges = create_mutation_range(func_settings, mutation_strength)
    gen_statistics = init_generation(childs, func_settings)

    for gen in range(generations):
        new_gen_statistics: dict[float, dict[str, int | float]] = {}
        child_id: int = 0

        gen_statistics = sorted(gen_statistics.items(), key=lambda item: item[1]["performance"], reverse=True)

        for mother in range(survivers):
            for offspring in range(childs / survivers):
                new_gen_statistics[child_id] = gen_statistics[mother][1]
                child_id += 1

        gen_statistics = new_gen_statistics

        for child in range(childs):
            mutated_args: dict[str, int | float] = \
            {
                key: values + randrange(-mutation_ranges[key], mutation_ranges[key], func_settings[key]["step"])
                for key, values in gen_statistics[child].items() if key != "total_net_worth"
            }

            performance: list[float] = func(data_frame, **{key: value for key, value in mutated_args if key != "total_net_worth"})
            true_performance: float = mean(performance)

            gen_statistics[child] = mutated_args
            gen_statistics[child]["performance"] = true_performance


def create_mutation_range(func_settings: dict[str, dict[str, int | float]], mutation_strength: float) -> dict[str, int | float]:
    """
    Creates a mutation range for each argument used in the indicator function.

    This function calculates the mutation range for each parameter based on its defined range (`start` to `end`) and the specified mutation strength.
    The mutation range is used to determine how much an argument can be altered during the mutation step of the genetic algorithm.

    :param func_settings: A dictionary defining the start, end, and step values for each parameter that the indicator function accepts.
        Each key is the name of the parameter, and the corresponding value is a dictionary with the structure:

        .. code-block:: python

            {
                "param_name": {"start": int, "end": int, "step": int}
            }

    :param mutation_strength: A float representing the proportion of the parameter range to use for mutation.
        For example, a mutation strength of 0.1 means 10% of the range will be used as the mutation range.

    :return: A dictionary with the same keys as `func_kwargs` but with values representing the calculated mutation range for each parameter.
        The mutation range is calculated as:

    :example:

        .. code-block:: python

            mutation_ranges = create_mutation_range(
                {
                    "short_period": {"start": 5, "end": 20, "step": 1},
                    "long_period": {"start": 20, "end": 50, "step": 5}
                },
                mutation_strength=0.1
            )
            print(mutation_ranges)
            # Output: {'short_period': 1.5, 'long_period': 3.0}
    """
    mutation_ranges: dict[str, int | float] = {
        key: (value["stop"] - value["start"]) * mutation_strength
        for key, value in func_settings.items()
    }

    return mutation_ranges


def init_generation(childs: int, func_settings: dict[str, dict[str, int | float]]) -> dict[float, dict[str, int | float]]:
    """
     Initializes the first generation of individuals with random values for each parameter.

     This function creates the initial population of individuals (strategies) for the genetic algorithm.
     Each individual is represented by a dictionary of parameters, initialized with random values between their specified ranges.
     Additionally, a default value of 1 is assigned to the `total_net_worth` for each individual.

     :param childs: The total number of individuals (children) to initialize in the first generation.

     :param func_settings: A dictionary defining the range (`start`, `end`, `step`) for each parameter used by the indicator function.
         Each key represents a parameter name, and its value is a dictionary with the following structure:

         .. code-block:: python

             {
                 "param_name": {"start": int, "end": int, "step": int}
             }

     :return: A dictionary where each key is an index representing an individual, and each value is a dictionary containing:
         - Randomly initialized parameters within the specified ranges.
         - A default `total_net_worth` of 1.
     """
    gen_statistics: dict[float, dict[str, int | float]] = []

    for child in range(childs):
        starting_args: dict[str, int | float] = {
            key: randrange(value["start"], value["stop"], value["step"])
            for key, value in func_settings.items(),
        }

        gen_statistics[child] = starting_args
        gen_statistics[child]["total_net_worth"] = 1

    return gen_statistics