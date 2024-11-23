from logging import getLogger

from pandas import Series

logger = getLogger("oracle.app")



def trend_based_pullback(indicator_series: Series, base_line: float, tolerance: float, lookback_window: int,
                         direction: str = 'both', return_pullback_strength: bool = False, magnitude_weight: float = 1,
                         rate_of_change_weight: float = 1) -> bool | float:
    """
    General function to detect trend-based pullbacks for any given indicator.

    :param indicator_series: The indicator series (e.g., MACD, EMA, RSI) to analyze.
    :param base_line: The line which the indicator should be considered to have "pulled back."
    :param tolerance: The allowed deviation to consider as a valid pullback.
    :param lookback_window: The number of periods to look back for potential pullback behavior.
        Automatically chooses the len(indicator_series) if lookback_period > len(indicator_series)
    :param direction: Direction of the pullback ('both', 'up', or 'down') from the threshold.
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

    if direction not in ['both', 'up', 'down']:
        raise AttributeError("Direction must be either both, up, or down.")

    if lookback_window < 0:
        raise AttributeError("Lookback period must be positive.")

    lookback_window = min(lookback_window, len(indicator_series))
    current_value = indicator_series.iloc[-1]

    pullback_found: bool = False
    pullback_direction: str = None

    value_entered_threshold_index: int = None
    value_above_threshold_index: int = None

    if direction in ['both', 'up']:
        if current_value > tolerance:
            for i in range(1, -lookback_window):
                current_value = indicator_series.iloc[-i]

                # Break if trend reverses (e.g., from positive to negative)
                if current_value < base_line:
                    break

                # Check if the indicator entered the threshold and then pulls back
                if base_line < current_value < tolerance:
                    value_entered_threshold_index = i
                # Check if the indicator entered the threshold and then pulls back
                elif current_value > tolerance:
                    value_above_threshold_index = i

                # Check if there was a value above the threshold before a value in the threshold
                if value_above_threshold_index is not None and value_entered_threshold_index is not None:
                    if value_above_threshold_index > value_entered_threshold_index:
                        pullback_direction = 'up'
                        pullback_found = True

    elif direction in ['both', 'down']:
        if current_value < -tolerance:
            for i in range(1, -lookback_window):
                current_value = indicator_series.iloc[-i]

                # Break if trend reverses (e.g., from negative to positive)
                if current_value > 0:
                    break

                # Check if the indicator entered the threshold and then pulls back
                if base_line > current_value > -tolerance:
                    value_entered_threshold_index = i
                # Check if the indicator entered the threshold and then pulls back
                elif current_value < -tolerance:
                    value_above_threshold_index = i

                # Check if there was a value below the threshold before a value in the threshold
                if value_above_threshold_index is not None and value_entered_threshold_index is not None:
                    if value_above_threshold_index < value_entered_threshold_index:
                        pullback_direction = 'down'
                        pullback_found = True

    if not return_pullback_strength or not pullback_found:
        return pullback_found

    if pullback_direction == 'up':
        closest_value_to_base_line = min(indicator_series.iloc[-value_above_threshold_index:])
    elif pullback_direction == 'down':
        closest_value_to_base_line = max(indicator_series.iloc[-value_above_threshold_index:])


    pullback_magnitude: float = abs(current_value - closest_value_to_base_line)
    max_magnitude: float = max(abs(indicator_series.max() - base_line), abs(indicator_series.min() - base_line))
    pullback_magnitude_signal: float = pullback_magnitude / max_magnitude

    pullback_index: int = indicator_series.iloc[-value_above_threshold_index:].index[indicator_series == closest_value_to_base_line].values[-1]
    rate_of_change: float = abs((current_value - closest_value_to_base_line)) / (len(indicator_series) - pullback_index)
    max_rate_of_change: float = max(abs(indicator_series.max() - indicator_series.min()) / lookback_window)
    rate_of_change_signal: float = rate_of_change / max_rate_of_change


    pullback_strength = (pullback_magnitude_signal * magnitude_weight +
                          rate_of_change_signal * rate_of_change_weight) / \
                        (magnitude_weight + rate_of_change_weight)

    logger.debug("Pullback found with a strength of " + str(pullback_strength))

    return pullback_strength
