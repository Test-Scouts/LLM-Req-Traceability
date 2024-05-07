from copy import copy
from functools import reduce
import json
import math


class Stats:
    def __init__(self, name: str, population: list[int | float]) -> None:
        self._name: str = name
        self._population: list[int | float] = copy(population)
        self._size: int = len(self._population)
        self._total: int | float | None

        # Mean undefined if empty population
        self._mean: float | None
        self._sd: float | None

        self._median: int | float | None
        self._quartiles: tuple[int | float | None, int | float | None]

        # Sort population to get min, max, and median
        sorted_population: list[int | float] = sorted(self._population)
        halves: tuple[list[int | float]]
        # Metrics undefined if empty population
        if not self._size:
            self._total = None
            self._min = None
            self._max = None
            self._mean = None
            self._median = None
            self._quartiles = (None, None)
            self._sd = None
        else:
            self._total = sum(self._population)
            self._min = sorted_population[0]
            self._max = sorted_population[-1]
            self._mean = self._total / self._size

            #      /--------------------
            #     / sum((xi - mean)^2)
            # _  / --------------------
            #  \/      population
            self._sd = math.sqrt(
                reduce(lambda acc, num: acc + (num - self._mean)**2, self._population, 0) / self._size
            )

            mid: int
            # No definite mid point, average of the 2 middle elements
            if self._size % 2 == 0:
                # The lower index of the 2 mid points
                mid = self._size//2 - 1
                # Even split
                halves = (sorted_population[:mid + 1], sorted_population[mid + 1:])
                self._median = (sorted_population[mid] + sorted_population[mid + 1]) / 2
            # Definite mid point, median exactly there
            else:
                # The exact mid point
                mid = self._size // 2
                # Split excl. mid
                halves = (sorted_population[:mid], sorted_population[mid + 1:])
                self._median = sorted_population[mid]

            # Size of the halves, both should be equal
            h_size: int = len(halves[0])

            # Check if halves are empty
            # Happens when the population only has 1 element because the median is excl.
            if not h_size:
                self._quartiles = (None, None)
                return

            h_mid: int
            q1: int | float
            q3: int | float

            # No definite mid point, average of the 2 middle elements
            if h_size % 2 == 0:
                # The lower index of the 2 mid points
                h_mid = h_size//2 - 1
                q1 = (halves[0][h_mid] + halves[0][h_mid + 1]) / 2
                q3 = (halves[1][h_mid] + halves[1][h_mid + 1]) / 2
            # Definite mid point, quartiles exactly there
            else:
                # The exact mid point
                h_mid = h_size // 2
                q1 = halves[0][h_mid]
                q3 = halves[1][h_mid]

            self._quartiles = (q1, q3)


    @property
    def name(self) -> str:
        return self._name

    @property
    def population(self) -> list[int | float]:
        return copy(self._population)

    @property
    def size(self) -> int:
        return self._size

    @property
    def total(self) -> int | float:
        return self._total

    @property
    def min(self) -> int | float:
        return self._min

    @property
    def max(self) -> int | float:
        return self._max

    @property
    def mean(self) -> float | None:
        return self._mean

    @property
    def median(self) -> int | float | None:
        return self._median
    
    @property
    def quartiles(self) -> tuple[int | float | None, int | float | None]:
        return self._quartiles

    @property
    def sd(self) -> float | None:
        return self._sd

    @property
    def as_dict(self) -> dict:
        return {
            "name": self._name,
            "population": self._population,
            "size": self._size,
            "total": self._total,
            "min": self._min,
            "q1": self._quartiles[0],
            "median": self._median,
            "q3": self._quartiles[1],
            "max": self._max,
            "mean": self._mean,
            "sd": self._sd
        }

    def __str__(self) -> str:
        return json.dumps(self.as_dict, indent=2)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(\"{self._name}\", {self._population})"
