import unittest
from example_module import (
    FloatDistribution,
    UniformDistribution,
    LogUniformDistribution,
    DiscreteUniformDistribution,
    IntDistribution,
    IntUniformDistribution,
    IntLogUniformDistribution,
    CategoricalDistribution,
    json_to_distribution,
    distribution_to_json,
    check_distribution_compatibility,
    _get_single_value,
    _convert_old_distribution_to_new_distribution,
    _is_distribution_log,
)

class TestFloatDistribution(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            FloatDistribution(low=1.0, high=-1.0)
        with self.assertRaises(ValueError):
            FloatDistribution(low=0.0, high=1.0, log=True)
        with self.assertRaises(ValueError):
            FloatDistribution(low=0.0, high=1.0, step=-1.0)

    def test_single(self):
        dist = FloatDistribution(low=1.0, high=1.0)
        self.assertTrue(dist.single())
        dist = FloatDistribution(low=1.0, high=2.0, step=1.0)
        self.assertFalse(dist.single())

    def test_contains(self):
        dist = FloatDistribution(low=1.0, high=3.0)
        self.assertTrue(dist._contains(2.0))
        self.assertFalse(dist._contains(-1.0))

    def test_to_internal_repr(self):
        dist = FloatDistribution(low=1.0, high=3.0)
        with self.assertRaises(ValueError):
            dist.to_internal_repr("a")
        self.assertEqual(dist.to_internal_repr(2.0), 2.0)

class TestUniformDistribution(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            UniformDistribution(low=-1.0, high=1.0)
        dist = UniformDistribution(low=1.0, high=3.0)
        self.assertEqual(dist.low, 1.0)
        self.assertEqual(dist.high, 3.0)

    def test_single(self):
        dist = UniformDistribution(low=1.0, high=1.0)
        self.assertTrue(dist.single())
        dist = UniformDistribution(low=1.0, high=2.0)
        self.assertFalse(dist.single())

class TestLogUniformDistribution(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            LogUniformDistribution(low=-1.0, high=1.0)
        with self.assertRaises(ValueError):
            LogUniformDistribution(low=0.0, high=1.0)

    def test_single(self):
        dist = LogUniformDistribution(low=1.0, high=1.0)
        self.assertTrue(dist.single())
        dist = LogUniformDistribution(low=1.0, high=2.0)
        self.assertFalse(dist.single())

class TestDiscreteUniformDistribution(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            DiscreteUniformDistribution(low=-1.0, high=1.0, q=1.0)

    def test_single(self):
        dist = DiscreteUniformDistribution(low=1.0, high=1.0, q=1.0)
        self.assertTrue(dist.single())
        dist = DiscreteUniformDistribution(low=1.0, high=2.0, q=1.0)
        self.assertFalse(dist.single())

class TestIntDistribution(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            IntDistribution(low=-1, high=1, log=True)
        with self.assertRaises(ValueError):
            IntDistribution(low=0, high=1, step=-1)

    def test_single(self):
        dist = IntDistribution(low=1, high=1, log=False)
        self.assertTrue(dist.single())
        dist = IntDistribution(low=1, high=2, log=False)
        self.assertFalse(dist.single())

class TestIntUniformDistribution(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            IntUniformDistribution(low=-1, high=1, step=1)

    def test_single(self):
        dist = IntUniformDistribution(low=1, high=1, step=1)
        self.assertTrue(dist.single())
        dist = IntUniformDistribution(low=1, high=2, step=1)
        self.assertFalse(dist.single())

class TestIntLogUniformDistribution(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            IntLogUniformDistribution(low=-1, high=1, step=1)

    def test_single(self):
        dist = IntLogUniformDistribution(low=1, high=1, step=1)
        self.assertTrue(dist.single())
        dist = IntLogUniformDistribution(low=1, high=2, step=1)
        self.assertFalse(dist.single())

class TestCategoricalDistribution(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            CategoricalDistribution(choices=[])

    def test_single(self):
        dist = CategoricalDistribution(choices=[True])
        self.assertTrue(dist.single())
        dist = CategoricalDistribution(choices=[True, False])
        self.assertFalse(dist.single())

class TestJsonToDistribution(unittest.TestCase):
    def test_json_to_distribution(self):
        json_str = '{"name": "FloatDistribution", "attributes": {"low": 1.0, "high": 3.0}}'
        dist = json_to_distribution(json_str)
        self.assertIsInstance(dist, FloatDistribution)

class TestDistributionToJson(unittest.TestCase):
    def test_distribution_to_json(self):
        dist = FloatDistribution(low=1.0, high=3.0)
        json_str = distribution_to_json(dist)
        self.assertEqual(json.loads(json_str), {"name": "FloatDistribution", "attributes": {"low": 1.0, "high": 3.0}})

class TestCheckDistributionCompatibility(unittest.TestCase):
    def test_check_distribution_compatibility(self):
        dist_old = FloatDistribution(low=1.0, high=3.0)
        dist_new = FloatDistribution(low=2.0, high=4.0)
        check_distribution_compatibility(dist_old, dist_new)

class TestGetSingleValue(unittest.TestCase):
    def test_get_single_value(self):
        dist = FloatDistribution(low=1.0, high=1.0)
        self.assertEqual(_get_single_value(dist), 1.0)

class TestConvertOldDistributionToNewDistribution(unittest.TestCase):
    def test_convert_old_distribution_to_new_distribution(self):
        distribution = UniformDistribution(low=1.0, high=3.0)
        new_dist = _convert_old_distribution_to_new_distribution(distribution)
        self.assertIsInstance(new_dist, FloatDistribution)

class TestIsDistributionLog(unittest.TestCase):
    def test_is_distribution_log(self):
        dist = FloatDistribution(low=1.0, high=3.0, log=True)
        self.assertTrue(_is_distribution_log(dist))

if __name__ == "__main__":
    unittest.main()