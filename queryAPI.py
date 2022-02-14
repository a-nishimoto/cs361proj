# API functions
from polygon import RESTClient
from datetime import datetime, date, timedelta

key = "XyYJRPzNQebo1mk_Kv9WvzSnjlVhWCQu"


def isClosed(date) -> bool:
    """
    determines if the specified date is a trading day
    date should be in YYYY-MM-DD format
    """

    # markets are closed on weekends
    d = datetime(date[0:4], date[5:7], date[8:])
    if d.weekday() > 4:
        return True

    # determine market holidays
    holidays = []
    try:
        # obtain list of market holidays from the API
        with RESTClient(key) as c:
            resp = c.reference_market_holidays()
            test = resp.marketholiday

        # check if today's date is in that list
        for holiday in test:
            if holiday.status == "closed":
                holidays.append(holiday.date)

        if date in holidays:
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
    """returns the latest price from the API"""

    # if market is closed, return data from the previous day's close
    with RESTClient(key) as c:
        res = c.stocks_equities_previous_close(ticker)
        res = res.results
        return res[0]['c']
