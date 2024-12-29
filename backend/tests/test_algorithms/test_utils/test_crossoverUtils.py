import pytest
from src.services.tradingComponents.indicators.utils import check_crossover


@pytest.mark.parametrize(
    "current_line1, current_line2, previous_line1, previous_line2, expected_result",
    [
        (1, 1, 1, 1, 0),
        (10, 2, 14, 6, 0),
        (2, 8, 14, 10, -1),
        (10, 8, 14, 18, 1)
    ]
)
def test_check_crossover(current_line1, current_line2, previous_line1, previous_line2, expected_result):
    assert check_crossover(current_line1, current_line2, previous_line1, previous_line2) == expected_result


def test_check_crossover_invalid_max_gradient_degree():
    with pytest.raises(ValueError) as ex:
        check_crossover(1, 2, 3, 4, True, 91, 1, 1)

    assert "max_gradient_degree must be between 0 and 90." in str(ex.value)

    with pytest.raises(ValueError) as ex:
        check_crossover(1, 2, 3, 4, True, -1, 1, 1)

    assert "max_gradient_degree must be between 0 and 90." in str(ex.value)


def test_check_crossover_invalid_weight_impact():
    with pytest.raises(ValueError) as ex:
        check_crossover(1, 2, 3, 4, True, 90, -1, 1.1)

    assert "weight_impact must be between 0 and 1." in str(ex.value)

    with pytest.raises(ValueError) as ex:
        check_crossover(1, 2, 3, 4, True, 90, 2, -0.1)

    assert "weight_impact must be between 0 and 1." in str(ex.value)


@pytest.mark.parametrize(
    "current_line1, current_line2, previous_line1, previous_line2, expected_result, max_gradient_degree, gradient_signal_weight, weight_impact",
    [
        (1, 1, 1, 1, 0, 90, 1, 1),
        (1, 5, 2, 7, 0, 90, 1, 1),
        (10, 8, 4, 6, 0.015618307215336302, 90, 1, 1),
        (4, 6, 10, 8, -0.015618307215336302, 90, 1, 1),
    ]
)
def test_check_crossover_strength(current_line1, current_line2, previous_line1, previous_line2, expected_result,
                                  max_gradient_degree, gradient_signal_weight, weight_impact):
    assert check_crossover(current_line1, current_line2, previous_line1, previous_line2, True,
                           max_gradient_degree, gradient_signal_weight, weight_impact) == expected_result
