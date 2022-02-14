from polygon import RESTClient

key = "XyYJRPzNQebo1mk_Kv9WvzSnjlVhWCQu"

with RESTClient(key) as client:
    resp = client.stocks_equities_daily_open_close("AAPL", "2021-06-11")
    print(
        f"On: {resp.from_} Apple opened at {resp.open} and closed at {resp.close}")
