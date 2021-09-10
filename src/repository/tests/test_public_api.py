import unittest

from .. import public_api


class TestCurrenciesMethods(unittest.TestCase):
    def test_get_currencies(self):
        data = public_api.getCurrencies()
        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
        self.assertTrue(len(data) > 0)

    def test_get_ticker(self):
        data = public_api.getTicker()
        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)


if __name__ == "__main__":
    unittest.main()
