from unittest import TestCase

from .stats import *


class TestStatsEmptyPopulation(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.stats: Stats = Stats("empty_population", [])

    def test_name(self):
        expected_name: str = "empty_population"
        actual_name: str = self.stats.name

        self.assertEqual(
            actual_name,
            expected_name,
            f"Expected: {expected_name}. Got: {actual_name}"
        )

    def test_is_empty_popuation(self):
        expected_population: list[int | float] = []
        actual_population: list[int | float] = self.stats.population

        self.assertListEqual(
            actual_population,
            expected_population,
            f"Expected: {expected_population}. Got: {actual_population}"
        )

    def test_is_zero_size(self):
        expected_size: int = 0
        actual_size: int = self.stats.size

        self.assertEqual(
            actual_size,
            expected_size,
            f"Expected: {expected_size}. Got: {actual_size}"
        )
    
    def test_is_undefined_metrics(self):
        self.assertIsNone(
            self.stats.min,
            "min should be None"
        )

        self.assertIsNone(
            self.stats.median,
            "median should be None"
        )

        self.assertIsNone(
            self.stats.max,
            "max should be None"
        )

        self.assertTupleEqual(
            self.stats.quartiles,
            (None, None),
            "quartiles should be (None, None)"
        )

        self.assertIsNone(
            self.stats.sd,
            "sd should be None"
        )

        self.assertIsNone(
            self.stats.mean,
            "mean should be None"
        )

    def test_as_dict(self):
        expected_dict: dict = {
            "name": "empty_population",
            "population": [],
            "size": 0,
            "total": None,
            "min": None,
            "q1": None,
            "median": None,
            "q3": None,
            "max": None,
            "mean": None,
            "sd": None
        }
        actual_dict: dict = self.stats.as_dict

        self.assertDictEqual(
            actual_dict,
            expected_dict,
            f"Expected: {expected_dict}. Got: {actual_dict}"
        )
