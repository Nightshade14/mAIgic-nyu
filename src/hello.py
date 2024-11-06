"""Dummy file to check ruff, pytest and automatic tests with CircleCI."""


def addition(num1: int, num2: int) -> int:
    """Add 2 numebrs and return their sum."""
    return num1 + num2


def main() -> int:
    """Contain the main execution logic."""
    n1 = 50
    n2 = 49
    return addition(n1, n2)


if __name__ == "__main__":
    main()
