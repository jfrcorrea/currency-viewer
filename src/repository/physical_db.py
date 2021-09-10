from datetime import datetime

import mysql.connector


class PhysicalDB():
    def __init__(self):
        self._conn = mysql.connector.connect(
            host="mysql",
            user="user",
            passwd="password",
            db="db"
        )
        cur = self._conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS `db`.`candles` (\n"
            "  `id` BIGINT(20) NOT NULL AUTO_INCREMENT,\n"
            "  `time_in_minutes` INT NOT NULL,\n"
            "  `currency_pair` VARCHAR(45) NOT NULL,\n"
            "  `candle_timestamp` TIMESTAMP NOT NULL,\n"
            "  `open` DOUBLE NULL,\n"
            "  `high` DOUBLE NULL,\n"
            "  `low` DOUBLE NULL,\n"
            "  `close` DOUBLE NULL,\n"
            "  PRIMARY KEY (`id`))\n"
        )

    def __del__(self):
        self._conn.close()

    def push_candle(self, currency_pair, time_in_minutes, timestamp, candle):
        cur = self._conn.cursor()

        str_timestamp = \
            datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(
            "insert into `db`.`candles`\n"
            "   (currency_pair, time_in_minutes, candle_timestamp, open,\n"
            "    high, low, close)\n"
            "values\n"
            "   (%s, %s, %s, %s, %s, %s, %s)\n",
            (currency_pair,
             time_in_minutes,
             str_timestamp,
             candle["open"],
             candle["high"],
             candle["low"],
             candle["close"])
        )
        self._conn.commit()
