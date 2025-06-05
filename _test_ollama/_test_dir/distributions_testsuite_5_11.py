import unittest
from distributions import FloatDistribution, UniformDistribution, LogUniformDistribution, DiscreteUniformDistribution, CategoricalDistribution, IntDistribution, IntLogUniformDistribution, IntUniformDistribution
from distributions import _adjust_discrete_uniform_high, _adjust_int_uniform_high


class TestFloatDistribution(unittest.TestCase):
    def setUp(self) -> None:
        self.test_instance = FloatDistribution(low=0.1, high=10.0)

    def test__init__(self) -> None:
        self.assertEqual(self.test_instance.low, 0.1)
        self.assertEqual(self.test_instance.high, 10.0)
        self.assertFalse(self.test_instance.log)
        self.assertIsNone(self.test_instance.step)

    def test_single(self) -> None:
        self.assertTrue(self.test_instance.single())

    def test_contains(self) -> None:
        self.assertTrue(self.test_instance._contains(5.0))
        self.assertFalse(self.test_instance._contains(-1.0))

    def test_to_internal_repr(self) -> None:
        self.assertEqual(self.test_instance.to_internal_repr(5.0), 5.0)
        with self.assertRaises(ValueError):
            self.test_instance.to_internal_repr("five")

    def test_to_external_repr(self) -> None:
        self.assertEqual(self.test_instance.to_external_repr(5.0), 5.0)


class TestUniformDistribution(unittest.TestCase):
    def setUp(self) -> None:
        self.test_instance = UniformDistribution(low=0.1, high=10.0)

    def test__init__(self) -> None:
        self.assertEqual(self.test_instance.low, 0.1)
        self.assertEqual(self.test_instance.high, 10.0)
        self.assertFalse(self.test_instance.log)
        self.assertIsNone(self.test_instance.step)

    def test_single(self) -> None:
        self.assertTrue(self.test_instance.single())

    def test_contains(self) -> None:
        self.assertTrue(self.test_instance._contains(5.0))
        self.assertFalse(self.test_instance._contains(-1.0))

    def test_to_internal_repr(self) -> None:
        self.assertEqual(self.test_instance.to_internal_repr(5.0), 5.0)
        with self.assertRaises(ValueError):
            self.test_instance.to_internal_repr("five")

    def test_to_external_repr(self) -> None:
        self.assertEqual(self.test_instance.to_external_repr(5.0), 5.0)


class TestLogUniformDistribution(unittest.TestCase):
    def setUp(self) -> None:
        self.test_instance = LogUniformDistribution(low=1e-10, high=10000000)

    def test__init__(self) -> None:
        self.assertEqual(self.test_instance.low, 1e-10)
        self.assertEqual(self.test_instance.high, 10000000)
        self.assertTrue(self.test_instance.log)
        self.assertIsNone(self.test_instance.step)

    def test_single(self) -> None:
        self.assertTrue(self.test_instance.single())

    def test_contains(self) -> None:
        self.assertTrue(self.test_instance._contains(5.0))
        self.assertFalse(self.test_instance._contains(-1e-10))

    def test_to_internal_repr(self) -> None:
        self.assertEqual(self.test_instance.to_internal_repr(5.0), 5.0)
        with self.assertRaises(ValueError):
            self.test_instance.to_internal_repr("five")

    def test_to_external_repr(self) -> None:
        self.assertEqual(self.test_instance.to_external_repr(5.0), 5.0)


class TestDiscreteUniformDistribution(unittest.TestCase):
    def setUp(self) -> None:
        self.test_instance = DiscreteUniformDistribution(low=1, high=10)

    def test__init__(self) -> None:
        self.assertEqual(self.test_instance.low, 1)
        self.assertEqual(self.test_instance.high, _adjust_int_uniform_high(1, 10, 2))
        self.assertFalse(self.test_instance.log)
        self.assertEqual(self.test_instance.step, 2)

    def test_single(self) -> None:
        self.assertTrue(self.test_instance.single())

    def test_contains(self) -> None:
        self.assertTrue(self.test_instance._contains(5.0))
        self.assertFalse(self.test_instance._contains(-1))

    def test_to_internal_repr(self) -> None:
        self.assertEqual(self.test_instance.to_internal_repr(5.0), 5.0)
        with self.assertRaises(ValueError):
            self.test_instance.to_internal_repr("five")

    def test_to_external_repr(self) -> None:
        self.assertEqual(self.test_instance.to_external_repr(5.0), 5.0)


class TestIntDistribution(unittest.TestCase):
    def setUp(self) -> None:
        self.test_instance = IntDistribution(low=1, high=10)

    def test__init__(self) -> None:
        self.assertEqual(self.test_instance.low, 1)
        self.assertEqual(self.test_instance.high, _adjust_int_uniform_high(1, 10, 2))
        self.assertFalse(self.test_instance.log)
        self.assertEqual(self.test_instance.step, 2)

    def test_single(self) -> None:
        self.assertTrue(self.test_instance.single())

    def test_contains(self) -> None:
        self.assertTrue(self.test_instance._contains(5.0))
        self.assertFalse(self.test_instance._contains(-1))

    def test_to_internal_repr(self) -> None:
        self.assertEqual(self.test_instance.to_internal_repr(5), 5)
        with self.assertRaises(ValueError):
            self.test_instance.to_internal_repr("five")

    def test_to_external_repr(self) -> None:
        self.assertEqual(self.test_instance.to_external_repr(5), 5)


class TestIntLogUniformDistribution(unittest.TestCase):
    def setUp(self) -> None:
        self.test_instance = IntLogUniformDistribution(low=1, high=10)

    def test__init__(self) -> None:
        self.assertEqual(self.test_instance.low, 1)
        self.assertEqual(self.test_instance.high, _adjust_int_uniform_high(1, 10, 2))
        self.assertTrue(self.test_instance.log)
        self.assertEqual(self.test_instance.step, 2)

    def test_single(self) -> None:
        self.assertTrue(self.test_instance.single())

    def test_contains(self) -> None:
        self.assertTrue(self.test_instance._contains(5.0))
        self.assertFalse(self.test_instance._contains(-1))

    def test_to_internal_repr(self) -> None:
        self.assertEqual(self.test_instance.to_internal_repr(5), 5)
        with self.assertRaises(ValueError):
            self.test_instance.to_internal_repr("five")

    def test_to_external_repr(self) -> None:
        self.assertEqual(self.test_instance.to_external_repr(5), 5)


class TestIntUniformDistribution(unittest.TestCase):
    def setUp(self) -> None:
        self.test_instance = IntUniformDistribution(low=1, high=10)

    def test__init__(self) -> None:
        self.assertEqual(self.test_instance.low, 1)
        self.assertEqual(self.test_instance.high, _adjust_int_uniform_high(1, 10, 2))
        self.assertFalse(self.test_instance.log)
        self.assertEqual(self.test_instance.step, 2)

    def test_single(self) -> None:
        self.assertTrue(self.test_instance.single())

    def test_contains(self) -> None:
        self.assertTrue(self.test_instance._contains(5.0))
        self.assertFalse(self.test_instance._contains(-1))

    def test_to_internal_repr(self) -> None:
        self.assertEqual(self.test_instance.to_internal_repr(5), 5)
        with self.assertRaises(ValueError):
            self.test_instance.to_internal_repr("five")

    def test_to_external_repr(self) -> None:
        self.assertEqual(self.test_instance.to_external_repr(5), 5)


class TestCategoricalDistribution(unittest.TestCase):
    def setUp(self) -> None:
        self.test_instance = CategoricalDistribution(choices=["a", "b"])

    def test__init__(self) -> None:
        self.assertEqual(self.test_instance.choices, ["a", "b"])

    def test_single(self) -> None:
        self.assertFalse(self.test_instance.single())

    def test_contains(self) -> None:
        self.assertTrue(self.test_instance._contains(0))
        self.assertFalse(self.test_instance._contains(-1))

    def test_to_internal_repr(self) -> None:
        self.assertEqual(self.test_instance.to_internal_repr("a"), 0)
        with self.assertRaises(ValueError):
            self.test_instance.to_internal_repr("five")

    def test_to_external_repr(self) -> None:
        self.assertEqual(self.test_instance.to_external_repr(0), "a")


class TestModuleFunctions(unittest.TestCase):
    def test_adjust_discrete_uniform_high(self) -> None:
        self.assertAlmostEqual(_adjust_discrete_uniform_high(1, 10, 2), 8)

    def test_adjust_int_uniform_high(self) -> None:
        self.assertEqual(_adjust_int_uniform_high(1, 10, 2), 8)


if __name__ == "__main__":
    unittest.main()