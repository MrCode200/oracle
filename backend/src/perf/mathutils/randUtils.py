from random import randrange


def randfloat(start: float, end: float, step: float = 1) -> float:
    """
    Generates a random float between the specified `start` and `end` values,
    with the given `step` size.

    Note that the `end` value is excluded from the possibilities if it's not
    a multiple of `step`.

    For example, with `start=0`, `end=99`, and `step=2`, the possible values
    will be 0, 2, 4, ..., 98. The function will never generate 99, as it's
    not a multiple of 2.

    :param start: The starting value of the range (inclusive).
    :param end: The ending value of the range (exclusive).
    :param step: The step size between the generated values.

    :return: A random float from the possible values in the range `[start, end)`
             with the given step size.
    :raise: ValueError: If `end` is less than `start`.
    """
    if end < start:
        raise ValueError("`end` argument must be greater than `start` argument")

    possibilities: int = int((end - start) / step)

    return start + (step * randrange(0, possibilities))
