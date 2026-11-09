import pytest

from solution import clamp


@pytest.mark.parametrize("value, lower, upper, expected", [
    (5, 0, 10, 5),
    (-2, 0, 10, 0),
    (12, 0, 10, 10),
    (0, 0, 10, 0),
    (10, 0, 10, 10),
    (4, 3, 3, 3),
    (-5, -10, -2, -5),
    (1.5, 0.0, 1.0, 1.0),
])
def test_clamp(value, lower, upper, expected):
    assert clamp(value, lower, upper) == expected


def test_inverted_bounds():
    with pytest.raises(ValueError):
        clamp(5, 10, 0)
