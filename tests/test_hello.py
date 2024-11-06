"""File tests hello.py file."""

from src.hello import addition, main


def test_addition() -> None:
    """Test the addition function."""
    test_7 = 7
    test_0 = 0
    test_negative_2 = -2
    assert addition(3, 4) == test_7
    assert addition(-1, 1) == test_0
    assert addition(-1, -1) == test_negative_2


def test_main() -> None:
    """Test the main function's behavior."""
    test_99 = 99
    assert main() == test_99  # 50 + 49 = 99
