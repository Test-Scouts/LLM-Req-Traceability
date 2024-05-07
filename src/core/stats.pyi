"""
Core module for calculating and formatting statistical values.

Includes:
---------
`Stats` - A class that calculates and formats statistical data.
"""


class Stats:
    """
    Represents statistical data of a collection of numbers, given that the points are normally distributed.

    `Stats.__str__` returns a formatted JSON string with each property as a field.

    Properties:
    -----------
    `readonly name: str` - The name of the population.\n
    `readonly population: list[int | float]` - A copy of the the population.\n
    `readonly size: int` - The size of the population.\n
    `readonly total: int | float | None` - The sum of the values of the entire population if not empty, else `None`.\n
    `readonly min: int | float | None` - The minimum value of the population if not empty, else `None`.\n
    `readonly max: int | float | None` - The maximum value of the population if not empty, else `None`.\n
    `readonly mean: float | None` - The mean value of the population if not empty, else `None`.\n
    `readonly median: int | float | None` - The median value of the population if not empty, else `None`.\n
    `readonly quartiles: tuple[int | float, int | float] | None` - The 25th and 75th percentiles of the population if applicable, else `None`.\n
    `readonly sd: float | None` - The standard deviation of the population if not empty, else `None`.\n
    `readonly as_dict: dict` - A dict representation of the stats.
    """
    def __init__(self, name: str, population: list[int | float]) -> None:
        ...

    @property
    def name(self) -> str:
        """
        The name of the population.
        """
        ...

    @property
    def population(self) -> list[int | float]:
        """
        A copy of the the population.
        """
        ...

    @property
    def size(self) -> int:
        """
        The size of the population.
        """
        ...

    @property
    def total(self) -> int | float | None:
        """
        The sum of the values of the entire population if not empty, else `None`.
        """
        ...

    @property
    def min(self) -> int | float:
        """
        The minimum value of the population if not empty, else `None`.
        """
        ...

    @property
    def max(self) -> int | float:
        """
        The maximum value of the population if not empty, else `None`.
        """
        ...

    @property
    def mean(self) -> float | None:
        """
        The mean value of the population if not empty, else `None`.
        """
        ...

    @property
    def median(self) -> int | float | None:
        """
        The median value of the population if not empty, else `None`.
        """
        ...

    @property
    def quartiles(self) -> tuple[int | float | None, int | float | None]:
        """
        The 25th and 75th percentiles of the population if applicable, else `(None, None)`.
        """

    @property
    def sd(self) -> float | None:
        """
        The standard deviation of the population if not empty, else `None`.
        """
        ...

    @property
    def as_dict(self) -> dict:
        """
        A dict representation of the stats.
        """
        ...

    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        ...
