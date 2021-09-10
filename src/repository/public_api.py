import requests


API_HOST = "https://poloniex.com/public"
API_LATENCY_IN_SECONDS = 1/6


def getCurrencies():
    querystring = {"command": "returnCurrencies"}
    try:
        response = requests.request("GET", API_HOST, params=querystring)
    except requests.exceptions.ConnectionError:
        return(None)
    currencies = response.json()
    return({key: value["name"] for key, value in currencies.items()})


def getTicker():
    querystring = {"command": "returnTicker"}
    try:
        response = requests.request("GET", API_HOST, params=querystring)
    except requests.exceptions.ConnectionError:
        return(None)
    ticker = response.json()
    return({key: value["last"]
            for key, value in ticker.items()
            if value["isFrozen"] == '0'})
