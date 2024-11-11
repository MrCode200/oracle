import random
from multiprocessing import Pool

from .mathutils import randfloat
from statistics import mean
import logging

from numpy.ma.core import arange

logger: logging.Logger = logging.getLogger("oracle.app")

def evolve(func: callable,
           func_settings: dict[str, dict[str, int | float]],
           default_arguments: dict[str, any],
           childs: int = 9,
           generations: int = 10,
           survivers: int = 3,
           mutation_strength: float = 0.1,
           mutation_probability: float = 0.5) -> dict[float, dict[str, int | float]]:
    """
    Evolves the optimal arguments for a given indicator function over multiple generations using a genetic algorithm approach.

    This function uses a genetic algorithm to optimize the arguments of a specified indicator function (`func`)
    applied to a financial dataset (`data_frame`). The optimization process aims to find the best-performing set of arguments
    that maximize the function's performance on the given dataset.

    The function initializes a population of individuals (each with a set of randomly generated arguments) and iteratively evolves them over several generations.
    In each generation, a subset of the best-performing individuals (survivors) are selected, and their arguments are mutated to produce offspring.
    The performance of each set of arguments is evaluated using the provided indicator function, and the process repeats for the specified number of generations.

    :param default_arguments: Arguments which will be always used and won't be mutated.

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

    :param mutation_probability: The probability of mutating an argument during the evolution process.
        A higher value means that more arguments will be mutated. Default is 0.5 (i.e., 50% of the arguments will be mutated).

    :raises ValueError: If `func_settings` does not contain the required keys ("start", "end", "step", "type") for each argument,
        if mutation_probability is not between 0 and 1,
        or if `childs` is not a multiple of `survivers`.

    :return: A a dict containing n-survivers best arguments for the function `func`.

    :example:

        .. code-block:: python

            import pandas as pd

            # Example usage
            data = pd.read_csv('financial_data.csv')
            settings = {
                "short_period": {"start": 5, "end": 15, "step": 1, "type": "int"},
                "long_period": {"start": 20, "end": 50, "step": 5, "type": "int"},
            }

            best_args = evolve(
                default_arguments=dict_of_default_arguments,
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
    required_keys = {"start", "stop", "step", "type"}
    for key, setting in func_settings.items():
        if not required_keys <= set(setting.keys()):  # Checks if all required keys are present
            raise ValueError(f"func_settings must contain dictionaries with the keys 'start', 'stop', and 'step'. Argument missing those keys: {key}")

    if childs % survivers != 0:
        raise ValueError("Childs must be a multiple of survivers")

    if mutation_probability < 0 or mutation_probability > 1:
        raise ValueError("mutation_probability must be between 0 and 1")

    mutation_ranges: dict[str, int | float] = create_mutation_range(func_settings, mutation_strength)
    gen_statistics = init_generation(childs, func_settings)

    for gen in range(generations):
        if gen > 0:
            gen_statistics = select_top_performers_and_reproduce(gen_statistics, survivers, childs)

        logger.error(f"Started generation {gen}/{generations} with candidates {gen_statistics}")

        for child in range(childs):
            child_id, child_statistics = evolve_child(child, gen_statistics[child], func, default_arguments,
                                                        func_settings, mutation_ranges, mutation_probability)
            gen_statistics[child_id] = child_statistics

    gen_statistics = select_top_performers_and_reproduce(gen_statistics, survivers, childs)
    winning_statistics = {}
    i: int = 0

    for child in range(childs):
        if i == 0:
            winning_statistics[child] = gen_statistics[child]
            i = int(childs/survivers) - 1
        else:
            i -= 1

    logger.error(f"Finished evolving generation {generations}/{generations}, with top candidates {winning_statistics}")

    return winning_statistics


def evolve_child(child_id: int, child: dict[str, int | float], func: callable, default_arguments: dict[str, any],
                   func_settings: dict[str, dict[str, int | float]], mutation_ranges: dict[str, int | float], mutation_probability: float):
    """
    Evaluates and mutates a single child in the population.

    :param child_id: The total number of offspring to generate in each generation. Must be a multiple of `survivers`.
        Default is 9.

    :param child: The current individual being evaluated.

    :param func: The indicator function to optimize. This function should accept keyword arguments corresponding to the argument names in `func_settings`
    and return a list of performance metrics (e.g., returns or profit/loss values).

    :param default_arguments: Arguments which will be always used and won't be mutated.

    :param func_settings: A dictionary that defines the range and step size for each argument used in the indicator function.
        Each key is the name of the argument, and the corresponding value is a dictionary with the following structure:

    :param mutation_ranges: The range of mutation applied to the arguments during the evolution process.

    :param mutation_probability: The probability of mutating an argument during the evolution process.
        A higher value means that more arguments will be mutated. Default is 0.5 (i.e., 50% of the arguments will be mutated).
    """
    mutated_args: dict[str, float] = \
        {
            key: values + randfloat(-mutation_ranges[key], mutation_ranges[key], func_settings[key]["step"])
            for key, values in child.items() if
            key != "performance" and random.random() < mutation_probability
        }

    mutated_args = \
        {
            key: int(value) if func_settings[key]["type"] == "int" else value
            for key, value in mutated_args.items()
        }

    performance: list[float] = func(**default_arguments,
                                    **{key: value for key, value in mutated_args.items() if key != "performance"})
    true_performance: float = mean(performance)

    child_statistics = mutated_args
    child_statistics["performance"] = true_performance

    return child_id, child_statistics


def create_mutation_range(func_settings: dict[str, dict[str, int | float]], mutation_strength: float) -> dict[str, int | float]:
    """
    Creates a mutation range for each argument used in the indicator function.

    This function calculates the mutation range for each parameter based on its defined range (`start` to `end`) and the specified mutation strength.
    The mutation range is used to determine how much an argument can be altered during the mutation step of the genetic algorithm.

    :param func_settings: A dictionary defining the start, end, and step values for each parameter that the indicator function accepts.
        Each key is the name of the parameter, and the corresponding value is a dictionary with the structure:

        .. code-block:: python

            {
                "param_name": {"start": int, "end": int, "step": int, "type": "int"}
            }

    :param mutation_strength: A float representing the proportion of the parameter range to use for mutation.
        For example, a mutation strength of 0.1 means 10% of the range will be used as the mutation range.

    :return: A dictionary with the same keys as `func_kwargs` but with values representing the calculated mutation range for each parameter.
        The mutation range is calculated as:

    :example:

        .. code-block:: python

            mutation_ranges = create_mutation_range(
                {
                    "param_name": {"start": 5, "end": 20, "step": 1, "type": "int"},
                    "param_name": {"start": 20, "end": 50, "step": 5, "type": "int"},
                    ...
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
     Additionally, a default value of 1 is assigned to the `performance` for each individual.

     :param childs: The total number of individuals (children) to initialize in the first generation.

     :param func_settings: A dictionary defining the range (`start`, `end`, `step`) for each parameter used by the indicator function.
         Each key represents a parameter name, and its value is a dictionary with the following structure:

         .. code-block:: python

             {
                 "param_name": {"start": int, "end": int, "step": int}
             }

     :return: A dictionary where each key is an index representing an individual, and each value is a dictionary containing:
         - Randomly initialized parameters within the specified ranges.
         - A default `performance` of 1.
     """
    gen_statistics: dict[float, dict[str, int | float]] = {}

    for child in range(childs):
        starting_args: dict[str, int | float] = {
            key: randfloat(value["start"], value["stop"], value["step"])
            for key, value in func_settings.items()
        }

        gen_statistics[child] = starting_args
        gen_statistics[child]["performance"] = 1

    return gen_statistics


def select_top_performers_and_reproduce(gen_statistics: dict[float, dict[str, int | float]], survivers: int, childs: int) -> dict[float, dict[str, int | float]]:
    """
    Selects the top-performing individuals from the current generation and replicates them to form the next generation.

    This function sorts the current generation of strategies based on their performance in descending order.
    It selects the top performers (survivers) and replicates each to produce offspring,
    filling the new generation with a total number of individuals equal to `childs`.

    :param gen_statistics:
        A dictionary where each key is an individual ID, and each value is a dictionary containing parameters and their performance.

        .. code-block:: python

            {
                0: {"param_name": 8, "param_name": 20, "performance": 8.5},
                1: {"param_name": 10, "param_name": 30, "performance": 15.2},
                ...
            }

    :param survivers: The number of top-performing individuals to retain and replicate.

    :param childs:The total number of individuals to be generated in the new generation. Must be a multiple of `survivers`.

    :return:
        A dictionary representing the new generation, with each key as a new individual ID and each value as a dictionary of parameters.

        .. code-block:: python

            {
                0: {"param_name": 8, "param_name": 30, "performance": 15.2},
                1: {"param_name": 10, "param_name": 50, "performance": 15.0},
                2: {"param_name": 5, "param_name": 20, "performance": 13.0},
                ...
            }
    """
    new_gen_statistics: dict[float, dict[str, int | float]] = {}
    child_id: int = 0

    gen_statistics = sorted(gen_statistics.items(), key=lambda item: item[1]["performance"], reverse=True)

    for mother in range(survivers):
        for offspring in range(int(childs / survivers)):
            new_gen_statistics[child_id] = gen_statistics[mother][1]
            child_id += 1

    return new_gen_statistics