import os
from stocks import Stock
import queryAPI
import json
import csv
import datetime
import time


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
            output[s['stock']] = (Stock(s['stock'], s['amount']))

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
        elif 'exit' in userInput:
            self.terminate()
        elif 'info' in userInput:
            self.showInfo()

    def display(self):
        """
        displays the stocks in a formatted manner
        """
        clearConsole()
        print("Hello, and welcome to this stock tracker tool \nCurrent time: ",
              datetime.datetime.now(), "\n")
        for item in self.data.values():
            print(item)
        print(
            "Options: Add Stock | Delete Stock | Modify Options Held | Get Stock Info | Export Data | Exit")
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
                self.modify()
            else:
                self.display()

        else:
            # check if this is a valid stock
            if queryAPI.check(stock) is False:
                print("Error: not a valid stock ticker")
                return self.display()

            self.data[stock] = Stock(stock, input(
                "Enter how many options you have: "))
            return self.display()

    def deleteStock(self):
        """
        deletes stock from the list
        """
        toDelete = input(
            "Please enter the ticker you wish to delete: ").upper()
        if toDelete not in self.data:
            print("Error: Stock is not in your list")
            self.display()

        else:
            confirm = input(
                f"Please confirm you are deleting {toDelete} Yes | No: ").lower()
            if confirm == 'yes':
                del self.data[toDelete]
                self.display()
            if confirm == 'no':
                self.display()

    def modify(self):
        """
        modifies an existing stock
        """
        clearConsole()
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
        if newAmount == 0:
            print("Editing to zero -- would you like to delete?")
            if input().lower() == 'yes':
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
        """exports """


if __name__ == "__main__":
    checkFile()
    data = read()
    Interface(data)
