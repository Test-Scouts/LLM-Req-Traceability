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
        self._min: int | float | None = min(self._population)
        self._max: int | float | None = max(self._population)

        # Mean undefined if empty population
        self._mean: float | None
        self._sd: float | None

        self._median: int | float | None

        mid: int = self._size // 2
        # Mean, median. and sd undefined if empty population
        if not self._size:
            self._total = None
            self._min = None
            self._max = None
            self._mean = None
            self._median = None
            self._sd = None
        else:
            self._total = sum(self._population)
            self._min = min(self._population)
            self._max = max(self._population)
            self._mean = self._total / self._size

            #      /--------------------
            #     / sum((xi - mean)^2)
            # _  / --------------------
            #  \/      population
            self._sd = math.sqrt(
                reduce(lambda acc, num: acc + (num - self._mean) ** 2, self._population, 0) / self._size
            )

            # No definite mid point, average of the 2 middle elements
            if self._size % 2 == 0:
                self._median = (self._population[mid] + self._population[mid + 1]) / 2
            # Definite mid point, median exactly there
            else:
                self._median = self._population[mid]

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
            "max": self._max,
            "mean": self._mean,
            "median": self._median,
            "sd": self._sd
        }

    def __str__(self) -> str:
        return json.dumps(self.as_dict(), indent=2)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(\"{self._name}\", {self._population})"
