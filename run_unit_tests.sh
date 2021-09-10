#!/bin/sh

python3 -m src.repository.tests.test_public_api
python3 -m src.repository.tests.test_cache_db
python3 -m src.repository.tests.test_physical_db

python3 -m src.service.tests.test_candles
