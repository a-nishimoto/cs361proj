import os
from stocks import Stock
import queryAPI
import json
import csv
import datetime
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


def clearConsole(): return os.system(
    'cls' if os.name in ('nt', 'dos') else 'clear')


def checkFile():
    """
    a file will save data between uses
    """

    if os.path.isfile('stocks.json'):
        # file exists
        return

    # stocks.json does not exist
    print("No data file found...creating new one")
    file = open('stocks.json', 'x')
    file.close()


def read():
    """
    reads the file into memory for use in our program
    """

    file = open('stocks.json')

    try:
        data = json.load(file)

        # create an array of Stock objects for future use
        output = {}
        for s in data:
            output[s['stock']] = (Stock(s['stock'], s['shares']))

    # process will fail if there is no data, this catches that
    except:
        output = None
        pass
    file.close()
    return output


class Interface:

    def __init__(self, data):
        self.data = data
        self.display()

    def prompt(self):
        userInput = input("What would you like to do: ").lower()
        if 'add' in userInput:
            self.addStock()
        elif 'delete' in userInput:
            self.deleteStock()
        elif 'modify' in userInput:
            self.modify()
        elif 'export' in userInput:
            self.export()
        elif 'info' in userInput:
            self.getStockInfo()
        elif 'quit' in userInput:
            self.quit()
        else:
            input("Invalid input: Press RETURN to try again: ")
            return self.display()

    def display(self):
        """
        displays the stocks in a formatted manner
        """
        clearConsole()
        print("Hello, and welcome to this stock tracker tool \nCurrent time: ",
              datetime.datetime.now(), "\n")
        totalHoldings = 0

        if self.data is None:
            self.data = dict()
            print("Stock watchlist is empty")

        for item in self.data.values():
            print(item)
            totalHoldings += item.value
        print(f"Current total holdings: ${round(totalHoldings, 2)}")

        print(
            "\nOptions: Add Stock | Delete Stock | Modify Options Held | Get Stock Info | Export Data | Quit")
        self.prompt()

    def addStock(self):
        """
        add a stock to the list
        """
        clearConsole()
        stock = input(
            "Please enter the stock ticker you wish to add: ").upper()

        if stock in self.data:
            modify = input(
                "Stock already logged. Would you like to modify? ").lower()
            if modify == 'yes':
                self.modify(stock)
            else:
                self.display()

        else:
            # check if this is a valid stock
            if queryAPI.check(stock) is False:
                print("Error: not a valid stock ticker. Returning to home screen")
                time.sleep(3)
                return self.display()

            self.data[stock] = Stock(stock, input(
                "Enter how many options you have: "))
            return self.display()

    def deleteStock(self):
        """
        deletes stock from the list
        """
        if len(self.data) == 0:
            input("Nothing to delete here: Press RETURN to go back ")
            return self.display()

        toDelete = input(
            "Please enter the ticker you wish to delete, or 'CANCEL' to go back: ").upper()
        if toDelete == "CANCEL":
            return self.display()
        if toDelete not in self.data:
            print("Error: Stock is not in your list, returning to home screen")
            time.sleep(3)
            self.display()

        else:
            confirm = input(
                f"Please confirm you are deleting {toDelete} --- Yes | No: ").lower()
            if confirm == 'yes':
                del self.data[toDelete]
                self.display()
            if confirm == 'no':
                self.display()

    def modify(self, toModify=None):
        """
        modifies an existing stock
        """
        if toModify is None:
            toModify = input("Enter the stock you want to modify: ")

        # not in the list
        if toModify not in self.data:
            print("This stock is not listed")
            add = input("Would you like to add it? Yes | No ").lower()
            if add == 'yes':
                return self.addStock()
            else:
                return self.display()

        newAmount = input("Please enter the new amount of stocks you hold: ")
        if newAmount == "0":
            print("Editing to zero -- would you like to delete?")
            if input("Yes | No --- ").lower() == 'yes':
                del self.data[toModify]
                return self.display()
            else:
                print("Stock will not be deleted or modified. Returning to home screen")
                return self.display()

        else:
            self.data[toModify].updateShares(newAmount)
            print(
                f"Modifying stock {toModify} with new amount held of {newAmount}")
            time.sleep(2)
            return self.display()

    def export(self):
        """exports stock data - ticker, current price, price 1 year ago, % gain: in the form of a CSV"""
        clearConsole()

        if len(self.data) == 0:
            input("Nothing to export. Please press ENTER to go back: ")
            return self.display()

        # ensure that user wants to export
        if input("Exporting data to CSV. \nThis will over-write any existing CSV file, be careful! \nPlease type PROCEED to export: ").upper() != "PROCEED":
            print('Cancelling process...returning to home screen!')
            time.sleep(3)
            return self.display()

        # prepare payload
        fields = ['Stock Ticker', 'Current Price',
                  'Price 1 Year Ago', 'Annual Percent Gain']
        rows = []

        for stock in self.data.values():
            prevPrice = queryAPI.priceNDaysBefore(stock.ticker, 365)
            percentage = (stock.currentPrice - prevPrice) / prevPrice * 100

            rows.append(
                [stock.ticker, stock.currentPrice, prevPrice, percentage])

        # write payload to CSV
        with open('stocks.csv', 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(fields)
            csvwriter.writerows(rows)

        print("Export complete...returning to home screen")
        time.sleep(3)
        return self.display()

    def getStockInfo(self):
        """
        gets a brief summary of the company scraped from the wikipedia page
        this is where I integrate someone else's microservice
        """

        s = input(
            "Please enter stock ticker to get info about the company: ").upper()
        if s not in self.data:
            print("Stock is not in your watchlist")
            time.sleep(2)
            return self.display()

        print(f"Getting information about {queryAPI.getName(s)}. Please wait")

        # integrate someone's microservice here
        time.sleep(4)

        print("Information found!")

        with open('input.txt', 'r') as file:
            contents = file.read()
            print(contents)

        input("Please press enter to return to main screen")
        return self.display()

    def quit(self):
        """exits the program safely, saving the data"""
        print("Exiting program...Your data will be automatically saved")
        if input("Please confirm: Yes | No : ").lower() == "yes":

            # prepare stock data into a payload for JSON saving
            json_data = []
            for s in self.data.values():
                d = dict()
                d["stock"] = s.ticker
                d["shares"] = s.shares
                json_data.append(d)

            # dump to JSON file
            with open('stocks.json', 'w') as jsonFile:
                json.dump(json_data, jsonFile)


if __name__ == "__main__":
    checkFile()
    data = read()
    Interface(data)
