import queryAPI
import datetime


class Stock:

    def __init__(self, ticker: str, shares) -> None:
        self.ticker = ticker
        self.shares = float(shares)
        self.currentPrice = float(queryAPI.updateCurrentPrice(self.ticker))
        self.value = 0
        self.lastupdated = datetime.datetime.now()
        self.calcValue()

    def __str__(self) -> str:
        return f"Stock ticker: {self.ticker} | Shares held: {self.shares} | Current Value: ${self.value}"

    def calcValue(self):
        self.value = round((self.shares * self.currentPrice), 2)

    def updateShares(self, newShares) -> None:
        self.shares = float(newShares)
        self.lastupdated = datetime.datetime.now()
        self.calcValue()
