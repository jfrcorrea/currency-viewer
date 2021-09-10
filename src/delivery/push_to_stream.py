import redis


CANDLES_X_1_MIN = 5
CANDLES_X_5_MIN = 6
CANDLES_X_10_MIN = 7
HOST = "redis"


class CandleStream():
    def __init__(self, time_in_minutes):
        self.time_in_minutes = time_in_minutes
        if time_in_minutes == 1:
            self._db = redis.Redis(host=HOST, db=CANDLES_X_1_MIN)
        elif time_in_minutes == 5:
            self._db = redis.Redis(host=HOST, db=CANDLES_X_5_MIN)
        elif time_in_minutes == 10:
            self._db = redis.Redis(host=HOST, db=CANDLES_X_10_MIN)
        else:
            raise ValueError("incorrect time specification for candle")

    def push_candle(self, currency_pair, candle_time, candle):
        if candle:
            candle["time"] = candle_time
            self._db.xadd(currency_pair, candle)
