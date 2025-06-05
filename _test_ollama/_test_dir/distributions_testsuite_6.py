import unittest
from distributions import FloatDistribution, IntDistribution, CategoricalDistribution
from distributions import json_to_distribution, _convert_old_distribution_to_new_distribution


class TestBaseDistribution(unittest.TestCase):
    def setUp(self) -> None:
        self.test_instance = BaseDistribution()

    def test_to_external_repr(self) -> None:
        with self.assertRaises(NotImplementedError):
            self.test_instance.to_external_repr(None)

    def test_to_internal_repr(self) -> None:
        with self.assertRaises(NotImplementedError):
            self.test_instance.to_internal_repr(None)

    def test_single(self) -> None:
        with self.assertRaises(NotImplementedError):
            self.test_instance.single()

    def test_contains(self) -> None:
        with self.assertRaises(NotImplementedError):
            self.test_instance._contains(None)


class TestFloatDistribution(unittest.TestCase):
    def setUp(self) -> None:
        self.test_instance = FloatDistribution(low=0.5, high=1.0)

    def test_to_external_repr(self) -> None:
        self.assertEqual(self.test_instance.to_external_repr(0.75), 0.75)

    def test_to_internal_repr(self) -> None:
        self.assertEqual(self.test_instance.to_internal_repr(0.75), 0.75)

    def test_single(self) -> None:
        self.assertFalse(self.test_instance.single())

    def test_contains(self) -> None:
        self.assertTrue(self.test_instance._contains(0.75))


class TestIntDistribution(unittest.TestCase):
    def setUp(self) -> None:
        self.test_instance = IntDistribution(low=1, high=10)

    def test_to_external_repr(self) -> None:
        self.assertEqual(self.test_instance.to_external_repr(5), 5)

    def test_to_internal_repr(self) -> None:
        self.assertEqual(self.test_instance.to_internal_repr(5), 5.0)

    def test_single(self) -> None:
        self.assertFalse(self.test_instance.single())

    def test_contains(self) -> None:
        self.assertTrue(self.test_instance._contains(5))


class TestCategoricalDistribution(unittest.TestCase):
    def setUp(self) -> None:
        self.test_instance = CategoricalDistribution(choices=["a", "b"])

    def test_to_external_repr(self) -> None:
        self.assertEqual(self.test_instance.to_external_repr(0), "a")

    def test_to_internal_repr(self) -> None:
        self.assertEqual(self.test_instance.to_internal_repr("a"), 0.0)

    def test_single(self) -> None:
        self.assertTrue(self.test_instance.single())

    def test_contains(self) -> None:
        self.assertTrue(self.test_instance._contains(0))


class TestModuleFunctions(unittest.TestCase):
    def test_json_to_distribution(self) -> None:
        json_str = '{"name": "FloatDistribution", "attributes": {"low": 1.0, "high": 10.0}}'
        distribution = json_to_distribution(json_str)
        self.assertIsInstance(distribution, FloatDistribution)

    def test_convert_old_distribution_to_new_distribution(self) -> None:
        old_dist = UniformDistribution(low=1.0, high=10.0)
        new_dist = _convert_old_distribution_to_new_distribution(old_dist)
        self.assertIsInstance(new_dist, FloatDistribution)


if __name__ == "__main__":
    unittest.main()