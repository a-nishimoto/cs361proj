import os
from stocks import Stock
import queryAPI
import json
import csv
import datetime
import time


def clearConsole():
    return os.system('cls' if os.name in ('nt', 'dos') else 'clear')


def checkFile():

    if os.path.isfile('stocks.json'):
        return

    print("No data file found...creating new one")
    file = open('stocks.json', 'x')
    file.close()


def read():

    file = open('stocks.json')

    try:
        data = json.load(file)
        output = {}
        for s in data:
            output[s['stock']] = (Stock(s['stock'], s['shares']))

    except:
        output = None
        pass
    file.close()
    return output


def csvExport(filename: str, csvfields: list, csvrows: list):

    with open(f"{filename}", 'w') as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow(csvfields)
        csvwriter.writerows(csvrows)

    return


class Interface:

    def __init__(self, data):
        self.data = data
        self.display()

    def display(self):

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

    def prompt(self):

        actions = {
            'add': self.addStock,
            'delete': self.deleteStock,
            'modify': self.modify,
            'export': self.export,
            'info': self.getStockInfo,
            'quit': self.quit
        }

        userInput = input("What would you like to do: ").lower()

        for key in actions:
            if key in userInput:
                actions[key]()

        else:
            input("Invalid input: Press RETURN to try again: ")
            return self.display()

    def addStock(self):

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
            if queryAPI.check(stock) is False:
                print("Error: not a valid stock ticker. Returning to home screen")
                time.sleep(3)
                return self.display()

            self.data[stock] = Stock(stock, input(
                "Enter how many options you have: "))
            return self.display()

    def deleteStock(self):

        if len(self.data) == 0:
            input("Nothing to delete: Press RETURN to go back ")
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

        if toModify is None:
            toModify = input("Enter the stock you want to modify: ")

        if toModify not in self.data:
            print("This stock is not listed")
            if input("Would you like to add it? Yes | No ").lower() == 'yes':
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
        clearConsole()

        if len(self.data) == 0:
            input("Nothing to export. Please press ENTER to go back: ")
            return self.display()

        if input("Exporting data to CSV. \nThis will over-write any existing CSV file, be careful! \nPlease type PROCEED to export: ").upper() != "PROCEED":
            print('Cancelling process...returning to home screen!')
            time.sleep(3)
            return self.display()

        fields = ['Stock Ticker', 'Current Price',
                  'Price 1 Year Ago', 'Annual Percent Gain']
        rows = []

        for stock in self.data.values():
            prevPrice = queryAPI.priceNDaysBefore(stock.ticker, 365)
            percentage = (stock.currentPrice - prevPrice) / prevPrice * 100

            rows.append(
                [stock.ticker, stock.currentPrice, prevPrice, percentage])

        csvExport('stocks.csv', fields, rows)

        print("Export complete...returning to home screen")
        time.sleep(3)
        return self.display()

    def getStockInfo(self):
        # this is where I integrate someone else's microservice

        s = input(
            "Please enter stock ticker to get info about the company: ").upper()
        if s not in self.data:
            print("Stock is not in your watchlist")
            time.sleep(2)
            return self.display()

        print(f"Getting information about {queryAPI.getName(s)}. Please wait")

        toWrite = queryAPI.getName(s)
        toWrite = toWrite.replace(" ", "_")
        toWrite = toWrite.replace(".", "")

        with open('input.txt', 'w+') as file:
            file.write(f"https://en.wikipedia.org/wiki/{toWrite}")

        os.system('python WikiScraper.py')

        time.sleep(7)
        clearConsole()
        print("Information found! \n")

        with open('tester.txt', 'r') as file:
            contents = file.read()
            print(contents)

        input("Please press enter to return to main screen")
        return self.display()

    def quit(self):
        print("Exiting program...Your data will be automatically saved")
        if input("Please confirm: Yes | No : ").lower() == "yes":

            json_data = []
            for s in self.data.values():
                d = dict()
                d["stock"] = s.ticker
                d["shares"] = s.shares
                json_data.append(d)

            with open('stocks.json', 'w') as jsonFile:
                json.dump(json_data, jsonFile)


if __name__ == "__main__":
    checkFile()
    data = read()
    Interface(data)
