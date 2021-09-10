import unittest
from time import time, sleep

import redis

from .. import cache_db


# Redis must be running on localhost
class TestCacheMethods(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCacheMethods, self).__init__(*args, **kwargs)

        self.db_currencies = cache_db.CurrenciesDB()
        self.db_tickers = cache_db.TickersDB()
        self.db_candles_1_min = cache_db.CandlesDB(1)
        self.db_candles_5_min = cache_db.CandlesDB(5)
        self.db_candles_10_min = cache_db.CandlesDB(10)

    def test_get_currencies_db(self):
        self.assertIsInstance(self.db_currencies._db, redis.client.Redis)

    def test_get_tickers_db(self):
        self.assertIsInstance(self.db_tickers._db, redis.client.Redis)

    def test_get_candles_db(self):
        self.assertIsInstance(self.db_candles_1_min._db, redis.client.Redis)
        self.assertEqual(self.db_candles_1_min.time_in_minutes, 1)

        self.assertIsInstance(self.db_candles_5_min._db, redis.client.Redis)
        self.assertEqual(self.db_candles_5_min.time_in_minutes, 5)

        self.assertIsInstance(self.db_candles_10_min._db, redis.client.Redis)
        self.assertEqual(self.db_candles_10_min.time_in_minutes, 10)

        with self.assertRaises(ValueError):
            cache_db.CandlesDB(-1)

    def test_push_candle_1_min(self):
        self.db_candles_1_min._db.flushdb()

        mock_currency_pair = "XPTO"
        mock_time = time()
        mock_candle = {"open": 987.654,
                       "high": 1000.0,
                       "low": 900.0,
                       "close": 912.345}

        self.db_candles_1_min.push_candle(mock_currency_pair,
                                          mock_time,
                                          mock_candle)

        value = eval(self.db_candles_1_min._db.hget(mock_currency_pair,
                                                    mock_time))

        self.assertEqual(value, mock_candle)

    def test_currencies_initialize(self):
        # Clear currencies DB to test initialization
        self.db_currencies._db.flushdb()

        # Initialize currencies DB
        self.db_currencies.currencies_initialize()

        self.assertTrue(self.db_currencies._db.dbsize() > 0)

    def test_push_ticker(self):
        self.db_tickers._db.flushdb()

        mock_currency_pair = "XPTO"
        mock_price = 1234.56789

        self.db_tickers.push_ticker(mock_currency_pair, mock_price)
        self.assertEqual(self.db_tickers._db.exists(mock_currency_pair), 1)
        self.assertEqual(self.db_tickers._db.hlen(mock_currency_pair), 1)

        values = self.db_tickers._db.hvals(mock_currency_pair)
        self.assertEqual(float(values[0]), mock_price)

    def test_get_currency_pairs(self):
        mock_currency_pair_1 = "XPTO"
        mock_price_1 = 1234.56789

        mock_currency_pair_2 = "XYZ"
        mock_price_2 = 4321.98765

        self.db_tickers._db.flushdb()

        self.db_tickers.push_ticker(mock_currency_pair_1, mock_price_1)
        self.db_tickers.push_ticker(mock_currency_pair_2, mock_price_2)

        currency_pairs = self.db_tickers.get_currency_pairs()

        self.assertEqual(set(currency_pairs),
                         {mock_currency_pair_1, mock_currency_pair_2})

    def test_get_last_candle_1_min(self):
        self.db_candles_1_min._db.flushdb()

        mock_currency_pair = "XPTO"

        last_candle_time_none = self.db_candles_1_min.get_last_candle_time(
            mock_currency_pair
        )
        self.assertIsNone(last_candle_time_none)

        mock_candle = {"open": 987.654,
                       "high": 1000.0,
                       "low": 900.0,
                       "close": 912.345}

        self.db_candles_1_min.push_candle(mock_currency_pair,
                                          time(),
                                          mock_candle)
        last_candle_time_1 = self.db_candles_1_min.get_last_candle_time(
            mock_currency_pair
        )

        self.db_candles_1_min.push_candle(mock_currency_pair,
                                          time(),
                                          mock_candle)
        last_candle_time_2 = self.db_candles_1_min.get_last_candle_time(
            mock_currency_pair
        )

        self.assertGreater(last_candle_time_2, last_candle_time_1)

    def test_get_last_ticker_time(self):
        self.db_tickers._db.flushdb()

        mock_currency_pair = "XPTO"
        mock_price = 1234.56789

        self.db_tickers.push_ticker(mock_currency_pair, mock_price)
        last_ticker_1 = self.db_tickers.get_last_ticker_time(
            mock_currency_pair
        )

        self.db_tickers.push_ticker(mock_currency_pair, mock_price)
        last_ticker_2 = self.db_tickers.get_last_ticker_time(
            mock_currency_pair
        )

        self.assertGreater(last_ticker_2, last_ticker_1)

    def test_get_first_ticker_time(self):
        self.db_tickers._db.flushdb()

        mock_currency_pair = "XPTO"
        mock_price = 1234.56789

        self.db_tickers.push_ticker(mock_currency_pair, mock_price)
        first_ticker_1 = self.db_tickers.get_first_ticker_time(
            mock_currency_pair
        )

        self.db_tickers.push_ticker(mock_currency_pair, mock_price)
        first_ticker_2 = self.db_tickers.get_first_ticker_time(
            mock_currency_pair
        )

        self.assertEqual(first_ticker_2, first_ticker_1)

    def test_get_prices_by_range(self):
        self.db_tickers._db.flushdb()

        mock_currency_pair = "XPTO"
        for i in range(100):
            self.db_tickers.push_ticker(mock_currency_pair, i)
            sleep(0.001)

        times = self.db_tickers._db.hgetall(mock_currency_pair)
        last_time = float(max(times))
        first_time = float(min(times))
        mean_time = (last_time + first_time) / 2

        prices = self.db_tickers.get_prices_by_range(mock_currency_pair,
                                                     mean_time,
                                                     last_time)

        self.assertLess(len(prices), 100)

    def test_tickers_db_reset(self):
        self.db_tickers._db.flushall()

        mock_currency_pair = "XPTO"
        mock_price = 1234
        self.db_tickers.push_ticker(mock_currency_pair, mock_price)
        self.assertGreater(self.db_tickers._db.dbsize(), 0)

        self.db_tickers.reset()
        self.assertEqual(self.db_tickers._db.dbsize(), 0)

    def test_candles_db_reset(self):
        self.db_candles_1_min._db.flushall()

        mock_currency_pair = "XPTO"
        mock_candle = {"open": 987.654,
                       "high": 1000.0,
                       "low": 900.0,
                       "close": 912.345}
        self.db_candles_1_min.push_candle(mock_currency_pair,
                                          time(),
                                          mock_candle)
        self.assertGreater(self.db_candles_1_min._db.dbsize(), 0)

        self.db_candles_1_min.reset()
        self.assertEqual(self.db_candles_1_min._db.dbsize(), 0)

    def test_candles_db_get_num_candles(self):
        self.db_candles_1_min._db.flushdb()

        mock_currency_pair = "XPTO"
        self.assertEqual(
            self.db_candles_1_min.get_num_candles(mock_currency_pair),
            0
        )

        mock_candle = {"open": 987.654,
                       "high": 1000.0,
                       "low": 900.0,
                       "close": 912.345}
        self.db_candles_1_min.push_candle(mock_currency_pair,
                                          time(),
                                          mock_candle)
        self.assertGreater(
            self.db_candles_1_min.get_num_candles(mock_currency_pair),
            0
        )


if __name__ == "__main__":
    unittest.main()
