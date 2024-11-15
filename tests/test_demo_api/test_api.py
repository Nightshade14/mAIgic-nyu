"""File tests hello.py file."""

from maigic_nyu.demo_api.api import addition, substraction


def test_addition() -> None:
    """Test the addition function."""
    test_7 = 7
    test_0 = 0
    test__2 = -2
    assert addition(3, 4) == test_7
    assert addition(-1, 1) == test_0
    assert addition(-1, -1) == test__2


def test_substraction() -> None:
    """Test the addition function."""
    test_7 = 7
    test_0 = 0
    test_negative_2 = -2
    assert substraction(10, 3) == test_7
    assert substraction(-1, -1) == test_0
    assert substraction(-1, 1) == test_negative_2
