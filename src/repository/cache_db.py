from time import time

import redis

from src.repository import public_api


CURRENCIES_DB = 0
TICKERS_DB = 1
CANDLES_DB_1_MIN = 2
CANDLES_DB_5_MIN = 3
CANDLES_DB_10_MIN = 4
HOST = "redis"


def reset_all():
    redis_db = redis.Redis(host=HOST)
    redis_db.flushall()


class CurrenciesDB():
    def __init__(self):
        self._db = redis.Redis(host=HOST, db=CURRENCIES_DB)

    def currencies_initialize(self):
        self._db.flushdb()

        currencies = public_api.getCurrencies()
        if currencies:
            self._db.mset(currencies)


class TickersDB():
    def __init__(self):
        self._db = redis.Redis(host=HOST, db=TICKERS_DB)

    def push_ticker(self, currency_pair, price, ticker_time=None):
        if not ticker_time:
            ticker_time = time()
        self._db.hset(currency_pair, ticker_time, price)

    def get_currency_pairs(self):
        keys = self._db.keys()
        return([key.decode() for key in keys])

    def get_last_ticker_time(self, currency_pair):
        times = self._db.hkeys(currency_pair)
        last_time = max(times)
        return(float(last_time))

    def get_first_ticker_time(self, currency_pair):
        times = self._db.hkeys(currency_pair)
        first_time = min(times)
        return(float(first_time))

    def get_prices_by_range(self, currency_pair, first_time, last_time):
        tickers = self._db.hgetall(currency_pair)
        times = [float(ticker_time)
                 for ticker_time in tickers
                 if (float(ticker_time) >= first_time and
                     float(ticker_time) <= last_time)]
        if times:
            times.sort()
            prices = []
            for ticker_time in times:
                prices.append(float(tickers[str(ticker_time).encode()]))
            return(prices)
        else:
            return([])

    def reset(self):
        self._db.flushdb()


class CandlesDB():
    def __init__(self, time_in_minutes):
        self.time_in_minutes = time_in_minutes
        if time_in_minutes == 1:
            self._db = redis.Redis(host=HOST, db=CANDLES_DB_1_MIN)
        elif time_in_minutes == 5:
            self._db = redis.Redis(host=HOST, db=CANDLES_DB_5_MIN)
        elif time_in_minutes == 10:
            self._db = redis.Redis(host=HOST, db=CANDLES_DB_10_MIN)
        else:
            raise ValueError("incorrect time specification for candle")

    def push_candle(self, currency_pair, candle_time, candle):
        self._db.hset(currency_pair, candle_time, str(candle))

    def get_last_candle_time(self, currency_pair):
        times = self._db.hkeys(currency_pair)
        if times:
            last_time = max(times)
            return(float(last_time))
        else:
            return(None)

    def reset(self):
        self._db.flushdb()

    def get_num_candles(self, currency_pair):
        return(self._db.hlen(currency_pair))
