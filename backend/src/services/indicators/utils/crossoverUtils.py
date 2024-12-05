from logging import getLogger
from math import atan

logger = getLogger("oracle.app")

# TODO: if current_lines should be passed or the dataFrame and index
def check_crossover(
    current_line1: float,
    current_line2: float,
    previous_line1: float,
    previous_line2: float,
    return_strength: bool = False,
    max_gradient_degree: float = 90,
    gradient_signal_weight: float = 1.0,
    weight_impact: float = 1.0
) -> float:
    """
    Determines if a crossover has occurred between two lines over the last two data points.

    A crossover is detected when one line crosses above or below the other line between two consecutive values.
    The function assesses the direction of the crossover from the perspective of the first line (line1).

    Optionally, it can return the strength of the crossover based on the absolute difference
    between the lines at the current point compared to the previous point.

    :param current_line1: The latest value of the first line.
    :param current_line2: The latest value of the second line.
    :param previous_line1: The previous value of the first line.
    :param previous_line2: The previous value of the second line.
    :key return_strength: If True, also returns the strength of the crossover.
    :key max_gradient_degree: The maximum degree of the gradient which gets used to calculate the strength of the crossover.
    :key gradient_signal_weight: The weight used for the strength calculated based on the gradient.
    :key weight_impact: How strong the impact of the weights are on the crossover output. Example: 1 - (1- weight) * weight_impact

    :returns:
        - An integer representing the type of crossover:
            - 1 for a bullish crossover (from below to above).
            - -1 for a bearish crossover (from above to below).
            - 0 for no crossover.
        - If `return_strength` is True, returns a value between -1 and 1.
          Strength is a float value representing the magnitude of the crossover.

    :raises ValueError: If `max_gradient_degree` is not between 0 and 90.
        Or if `weight_impact` is not between 0 and 1.
    """
    if not 0 <= max_gradient_degree <= 90:
        raise ValueError("max_gradient_degree must be between 0 and 90.")

    if weight_impact < 0 or weight_impact > 1:
        raise ValueError("weight_impact must be between 0 and 1.")


    if (current_line1 >= current_line2) == (previous_line1 >= previous_line2):
        crossover_type: int = 0
    elif current_line1 > current_line2:
        crossover_type: int = 1
    else:
        crossover_type: int = -1

    if not return_strength and crossover_type != 0:
        return crossover_type


    gradient: float = (current_line1 - previous_line1)
    gradient_signal: float = abs(atan(gradient) / max_gradient_degree)
    gradient_signal = 1 if gradient_signal > 1 else gradient_signal

    total_weigths: float = gradient_signal_weight
    weights: float = 1 if total_weigths == 0 else (gradient_signal * gradient_signal_weight) / total_weigths

    return crossover_type * (1 - (1 - weights) * weight_impact)
