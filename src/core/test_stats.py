from unittest import TestCase

from .stats import *


class TestStatsIsDataClass(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.initial_population: list[int | float] = []
        self.stats: Stats = Stats("data_class", self.initial_population)
        self.setUpClass

    def test_immutable_population_on_init(self):
        tmp_population: list[int | float] = []
        tmp_stats: Stats = Stats("tmp_stats", tmp_population)

        for i in range(10):
            tmp_population.append(i)
        for i in range(5):
            tmp_population.pop(0)

        self.assertListEqual(
            tmp_stats.population,
            [],
            f"Population should be empty. Got: {tmp_stats.population}"
        )

    def test_immutable_population_property(self):
        population: list[int | float] = self.stats.population

        for i in range(10):
            population.append(i)
        for i in range(5):
            population.pop(0)

        self.assertListEqual(
            self.stats.population,
            self.initial_population,
            f"Population should be empty. Got: {self.stats.population}"
        )

    def test_immutable_name(self):
        def set_name():
            self.stats.name = "new_name"

        self.assertRaises(
            AttributeError,
            set_name
        )

    def test_immutable_min(self):
        def set_min():
            self.stats.min = 0
        
        self.assertRaises(
            AttributeError,
            set_min
        )

    def test_immutable_max(self):
        def set_max():
            self.stats.max = 0
        
        self.assertRaises(
            AttributeError,
            set_max
        )

    def test_immutable_quartiles_set(self):
        # Tuples' references are immutable, no need to check
        def set_quartiles():
            self.stats.quartiles = (0, 0)
        
        self.assertRaises(
            AttributeError,
            set_quartiles
        )

    def test_immutable_median(self):
        def set_median():
            self.stats.median = 0
        
        self.assertRaises(
            AttributeError,
            set_median
        )

    def test_immutable_mean(self):
        def set_mean():
            self.stats.mean = 0
        
        self.assertRaises(
            AttributeError,
            set_mean
        )

    def test_immutable_sd(self):
        def set_sd():
            self.stats.sd = 0
        
        self.assertRaises(
            AttributeError,
            set_sd
        )


class TestStatsEmptyPopulation(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.expected_population: list[int | float] = []
        self.stats: Stats = Stats("empty_population", self.expected_population)

    def test_name(self):
        expected_name: str = "empty_population"
        actual_name: str = self.stats.name

        self.assertEqual(
            actual_name,
            expected_name,
            f"Expected: {expected_name}. Got: {actual_name}"
        )

    def test_is_empty_popuation(self):
        expected_population: list[int | float] = self.expected_population
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

    def test_quartiles_is_tuple(self):
        self.assertTrue(
            isinstance(self.stats.quartiles, tuple),
            f"Quartiles should be a tuple. Got: {type(self.stats.quartiles).__name__}"
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


class TestStatsSingleIntEntryPopulation(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.entry: int = 0
        self.expected_population: list[int] = [self.entry]
        self.stats: Stats = Stats("single_int_entry", self.expected_population)

    def test_population_is_equal(self):
        self.assertListEqual(
            self.stats.population,
            [self.entry],
            f"Expected: {[self.entry]}. Got: {self.stats.population}"
        )

    def test_size_is_one(self):
        self.assertEqual(
            self.stats.size,
            1,
            f"Expected: 1. Got: {self.stats.size}"
        )

    def test_total_is_entry(self):
        self.assertEqual(
            self.stats.total,
            self.entry,
            f"Expected: {self.entry}. Got: {self.stats.total}"
        )

    def test_min_is_entry(self):
        self.assertEqual(
            self.stats.min,
            self.entry,
            f"Expected: {self.entry}. Got: {self.stats.min}"
        )

    def test_max_is_entry(self):
        self.assertEqual(
            self.stats.max,
            self.entry,
            f"Expected: {self.entry}. Got: {self.stats.max}"
        )

    def test_quartiles_are_none(self):
        self.assertTupleEqual(
            self.stats.quartiles,
            (None, None),
            f"Expected: {(None, None)}. Got: {self.stats.quartiles}"
        )

    def test_median_is_entry(self):
        self.assertEqual(
            self.stats.median,
            self.entry,
            f"Expected: {self.entry}. Got: {self.stats.median}"
        )

    def test_mean_is_entry(self):
        self.assertEqual(
            self.stats.mean,
            self.entry,
            f"Expected: {self.entry}. Got: {self.stats.mean}"
        )

    def test_sd_is_zero(self):
        self.assertEqual(
            self.stats.sd,
            0,
            f"Expected: 0. Got: {self.stats.sd}"
        )

    def test_as_dict(self):
        expected_dict: dict = {
            "name": "single_int_entry",
            "population": [self.entry],
            "size": 1,
            "total": self.entry,
            "min": self.entry,
            "q1": None,
            "median": self.entry,
            "q3": None,
            "max": self.entry,
            "mean": self.entry,
            "sd": 0
        }
        actual_dict: dict = self.stats.as_dict

        self.assertDictEqual(
            actual_dict,
            expected_dict,
            f"Expected: {expected_dict}. Got: {actual_dict}"
        )
