from logging import getLogger

logger = getLogger("oracle.app")


def check_crossover(
    current_line1: float,
    current_line2: float,
    previous_line1: float,
    previous_line2: float,
    return_strength: bool = False
) -> float:
    """
    Determines if a crossover has occurred between two lines over the last two data points.

    A crossover is detected when one line crosses above or below the other line between two consecutive values.
    The function assesses the direction of the crossover from the perspective of the first line.

    Optionally, it can return the strength of the crossover based on the absolute difference
    between the lines at the current point compared to the previous point.

    :param current_line1: The latest value of the first line.
    :param current_line2: The latest value of the second line.
    :param previous_line1: The previous value of the first line.
    :param previous_line2: The previous value of the second line.
    :param return_strength: If True, also returns the strength of the crossover.

    :returns:
        - An integer representing the type of crossover:
            - 1 for a bullish crossover (from below to above).
            - -1 for a bearish crossover (from above to below).
            - 0 for no crossover.
        - If `return_strength` is True, returns a tuple of (crossover_type, strength).
          Strength is a float value representing the magnitude of the crossover.
    """
    # Determine if a crossover occurred
    if (current_line1 > current_line2) == (previous_line1 > previous_line2):
        crossover_type = 0
    elif current_line1 > current_line2:
        crossover_type = 1
    else:
        crossover_type = -1

    if not return_strength:
        return crossover_type

    # Here code for returning the strength of the crossover

    return crossover_type

