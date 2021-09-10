import unittest
from time import time

from .. import candles
from ...repository import cache_db


class TestProcessCandles(unittest.TestCase):
    def test_process(self):
        tickers_db = cache_db.TickersDB()
        tickers_db.reset()

        candles_db_1_min = cache_db.CandlesDB(1)
        candles_db_5_min = cache_db.CandlesDB(5)
        candles_db_10_min = cache_db.CandlesDB(10)

        candles_db_1_min.reset()
        candles_db_5_min.reset()
        candles_db_10_min.reset()

        mock_currency_pair = "XPTO"
        mock_price = 123
        start_time = time()

        # Simulate 10 minutes of tickers, 1 ticker/s
        for minutes in range(10):
            for seconds in range(61):
                tickers_db.push_ticker(mock_currency_pair,
                                       mock_price,
                                       start_time + (seconds * (minutes+1)))

            candles.process()

        self.assertEqual(candles_db_1_min.get_num_candles(mock_currency_pair),
                         10)
        self.assertEqual(candles_db_5_min.get_num_candles(mock_currency_pair),
                         2)
        self.assertEqual(candles_db_10_min.get_num_candles(mock_currency_pair),
                         1)


if __name__ == "__main__":
    unittest.main()
