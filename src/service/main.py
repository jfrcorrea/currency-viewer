from datetime import datetime

from src.repository import public_api, cache_db
import src.service.candles as candles


def main():
    cache_db.reset_all()

    currencies_db = cache_db.CurrenciesDB()
    tickers_db = cache_db.TickersDB()

    currencies_db.currencies_initialize()

    last_ticker_datetime = datetime.now()
    while True:
        delta_from_last_ticker = datetime.now() - last_ticker_datetime
        seconds_from_last_ticker = (
            delta_from_last_ticker.seconds +
            delta_from_last_ticker.microseconds / 1000000
        )
        if seconds_from_last_ticker > public_api.API_LATENCY_IN_SECONDS:
            last_ticker_datetime = datetime.now()
            tickers = public_api.getTicker()
            if tickers:
                for currency_pair, price in tickers.items():
                    tickers_db.push_ticker(currency_pair, price)

                candles.process()


if __name__ == "__main__":
    main()
