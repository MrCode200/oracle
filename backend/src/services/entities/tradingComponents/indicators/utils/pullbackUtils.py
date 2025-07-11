from logging import getLogger

from pandas import Series

logger = getLogger("oracle.app")


# noinspection PyArgumentList
def trend_based_pullback(
    tc_series: Series,
    base_line: float,
    tolerance: float,
    lookback_window: int,
    direction: str = "both",
    return_pullback_strength: bool = False,
    magnitude_weight: float = 1,
    rate_of_change_weight: float = 1,
) -> bool | float:
    """
    General function to detect trend-based pullbacks for any given Trading Component.

    :param tc_series: The Trading Component series (e.g., MACD, EMA, RSI) to analyze.
    :param base_line: The line which the Trading Component should be considered to have "pulled back."
    :param tolerance: The allowed deviation to consider as a valid pullback.
    :param lookback_window: The number of periods to look back for potential pullback behavior.
        Automatically chooses the len(tc_series) if lookback_period > len(tc_series)
    :param direction: Direction of the pullback ('both', 'up', or 'down') from the limit.
    :param return_pullback_strength: Whether to return the strength of the pullback.
    :param magnitude_weight: The weight for the magnitude calculation.
    :param rate_of_change_weight: The weight for the rate of change calculation.

    :returns: True if a valid pullback is detected, otherwise False.
        Or a float representing the strength of the pullback if a valid pullback is detected. If not detected, returns False.

    :raises AttributeError: If tolerance is negative.
        If direction is neither both, up, nor down.
        If lookback_period is negative.
    """
    if tolerance < 0:
        raise AttributeError("Tolerance must be positive.")

    if direction not in ["both", "up", "down"]:
        raise AttributeError("Direction must be either both, up, or down.")

    if lookback_window < 0:
        raise AttributeError("Lookback period must be positive.")

    lookback_window = min(lookback_window, len(tc_series))
    current_value = tc_series.iloc[-1]

    pullback_found: bool = False
    pullback_direction: str = None

    value_entered_limit_index: int = None
    value_above_limit_index: int = None

    if direction in ["both", "up"]:
        if current_value > tolerance:
            for i in range(1, -lookback_window):
                current_value = tc_series.iloc[-i]

                # Break if trend reverses (e.g., from positive to negative)
                if current_value < base_line:
                    break

                # Check if the Trading Component entered the limit and then pulls back
                if base_line < current_value < tolerance:
                    value_entered_limit_index = i

                # Check if the Trading Component entered the limit and then pulls back
                elif current_value > tolerance:
                    value_above_limit_index = i

                # Check if there was a value above the limit before a value in the limit
                if (
                    value_above_limit_index is not None
                    and value_entered_limit_index is not None
                ):
                    if value_above_limit_index > value_entered_limit_index:
                        pullback_direction = "up"
                        pullback_found = True

    elif direction in ["both", "down"]:
        if current_value < -tolerance:
            for i in range(1, -lookback_window):
                current_value = tc_series.iloc[-i]

                # Break if trend reverses (e.g., from negative to positive)
                if current_value > 0:
                    break

                # Check if the Trading Component entered the limit and then pulls back
                if base_line > current_value > -tolerance:
                    value_entered_limit_index = i

                # Check if the Trading Component entered the limit and then pulls back
                elif current_value < -tolerance:
                    value_above_limit_index = i

                # Check if there was a value below the limit before a value in the limit
                if (
                    value_above_limit_index is not None
                    and value_entered_limit_index is not None
                ):
                    if value_above_limit_index < value_entered_limit_index:
                        pullback_direction = "down"
                        pullback_found = True

    if not return_pullback_strength or not pullback_found:
        return pullback_found

    if pullback_direction == "up":
        closest_value_to_base_line = min(
            tc_series.iloc[-value_above_limit_index:]
        )
    elif pullback_direction == "down":
        closest_value_to_base_line = max(
            tc_series.iloc[-value_above_limit_index:]
        )

    pullback_magnitude: float = abs(current_value - closest_value_to_base_line)
    max_magnitude: float = max(
        abs(tc_series.max() - base_line), abs(tc_series.min() - base_line)
    )
    pullback_magnitude_signal: float = pullback_magnitude / max_magnitude

    pullback_index: int = (
        tc_series.iloc[-value_above_limit_index:]
        .index[tc_series == closest_value_to_base_line]
        .values[-1]
    )
    rate_of_change: float = abs((current_value - closest_value_to_base_line)) / (
            len(tc_series) - pullback_index
    )
    max_rate_of_change: float = max(
        abs(tc_series.max() - tc_series.min()) / lookback_window
    )
    rate_of_change_signal: float = rate_of_change / max_rate_of_change

    pullback_strength = (
        pullback_magnitude_signal * magnitude_weight
        + rate_of_change_signal * rate_of_change_weight
    ) / (magnitude_weight + rate_of_change_weight)

    logger.debug("Pullback found with a strength of " + str(pullback_strength))

    return pullback_strength
