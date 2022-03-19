# API functions
from polygon import RESTClient
from datetime import date, timedelta

key = "XyYJRPzNQebo1mk_Kv9WvzSnjlVhWCQu"


def isClosed(date) -> bool:

    if date.weekday() > 4:  # work days are 0-4
        return True

    holidays = []
    try:
        # obtain list of market holidays from the API
        with RESTClient(key) as c:
            resp = c.reference_market_holidays()
            test = resp.marketholiday

        for holiday in test:
            if holiday.status == "closed":
                holidays.append(holiday.date)

        if str(date) in holidays:
            return True

    except:
        return "Unable to connect to service"

    return False


def check(ticker: str) -> bool:
    """checks if the stock ticker is valid"""

    try:
        with RESTClient(key) as c:
            resp = c.reference_ticker_details_vx(ticker)
            return True

    except:
        return False


def updateCurrentPrice(ticker: str):

    # if market is closed, return data from the previous day's close
    with RESTClient(key) as c:
        res = c.stocks_equities_previous_close(ticker)
        res = res.results
        return res[0]['c']


def priceNDaysBefore(ticker: str, days: int):

    curDate = date.today()
    prevDate = curDate - timedelta(days)

    while isClosed(prevDate):
        prevDate = prevDate - timedelta(1)

    with RESTClient(key) as c:
        res = c.stocks_equities_daily_open_close(ticker, str(prevDate))
        return res.close


def getName(ticker):
    with RESTClient(key) as c:
        resp = c.reference_ticker_details_vx(ticker)
        return resp.results['name']
