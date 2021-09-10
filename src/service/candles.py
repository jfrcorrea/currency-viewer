from src.repository import cache_db, physical_db
from src.delivery import push_to_stream


def process():
    tickers_db = cache_db.TickersDB()

    db = physical_db.PhysicalDB()

    for candle_time_in_minutes in [1, 5, 10]:
        candle_db = cache_db.CandlesDB(candle_time_in_minutes)
        stream = push_to_stream.CandleStream(candle_time_in_minutes)

        candle_time_in_seconds = candle_time_in_minutes * 60

        currency_pairs = tickers_db.get_currency_pairs()
        for currency_pair in currency_pairs:
            last_ticker_time = tickers_db.get_last_ticker_time(currency_pair)
            first_ticker_time = tickers_db.get_first_ticker_time(currency_pair)

            last_candle_time = candle_db.get_last_candle_time(
                currency_pair
            )
            if last_candle_time:
                lower_time = last_candle_time
            else:
                lower_time = first_ticker_time

            if lower_time + candle_time_in_seconds > last_ticker_time:
                # reach last candle and its incomplete
                # go to the next currency pair
                continue
            else:
                upper_time = lower_time + candle_time_in_seconds

            prices = tickers_db.get_prices_by_range(currency_pair,
                                                    lower_time,
                                                    upper_time)
            if prices:
                candle = {"open": prices[0],
                          "high": max(prices),
                          "low": min(prices),
                          "close": prices[-1]}
            else:
                candle = {"open": None,
                          "high": None,
                          "low": None,
                          "close": None}
            candle_db.push_candle(currency_pair, upper_time, candle)
            stream.push_candle(currency_pair, upper_time, candle)
            db.push_candle(currency_pair,
                           candle_db.time_in_minutes,
                           upper_time,
                           candle)
