import unittest
from time import time
from datetime import datetime
from math import trunc

import mysql.connector

from .. import physical_db


class TestPhysicalDB(unittest.TestCase):
    def test_physical_db_class(self):
        db = physical_db.PhysicalDB()
        self.assertIsInstance(db._conn,
                              mysql.connector.connection.MySQLConnection)

    def test_push_candle(self):
        db = physical_db.PhysicalDB()
        cur = db._conn.cursor()

        cur.execute("delete from `db`.`candles`")

        mock_currency_pair = "XPTO"
        mock_time_in_minutes = 1
        mock_timestamp = time()
        mock_candle = {"open": 123,
                       "high": 123,
                       "low": 123,
                       "close": 123}
        db.push_candle(mock_currency_pair,
                       mock_time_in_minutes,
                       mock_timestamp,
                       mock_candle)

        cur.execute(
            "select time_in_minutes,\n"
            "       currency_pair,\n"
            "       candle_timestamp,\n"
            "       open,\n"
            "       high,\n"
            "       low,\n"
            "       close\n"
            "  from `db`.`candles`\n"
        )
        row = cur.fetchone()

        dt_timestamp = datetime.fromtimestamp(trunc(mock_timestamp))
        self.assertEqual(row,
                         (mock_time_in_minutes,
                          mock_currency_pair,
                          dt_timestamp,
                          mock_candle["open"],
                          mock_candle["high"],
                          mock_candle["low"],
                          mock_candle["close"]))

        cur.execute("delete from `db`.`candles`")
        db._conn.commit()


if __name__ == "__main__":
    unittest.main()
