# Author: Marcus Kim
# Created: April 16, 2021
# Edited: March 5, 2022

import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from strategyUtil import *
pd.options.mode.chained_assignment = None  # default='warn'

# -------------------------- CONFIGURE SETTINGS --------------------------

lineRelevanceLength = 99990
sellAtLoss = False
rangeSize = 11

stYear = 2016
stMonth = 1
stDay = 1
singleTest = True
testNow = True
beforeCovid = dt.datetime(2020, 1, 1)

# ------------------------------------------------------------------------

stockList = []
numStocks = len(stockList)
summary = 0

if singleTest:
    stockList.append(input("Enter Ticker: "))
    print(stockList[0])
else:
    root = Tk()
    fileTypes = [("Text Files", "*.txt")]
    title = "Title"
    defaultDirectory = r"C:\Users\adam\Documents\python\stockLists"
    filePath = askopenfilename(filetypes=fileTypes, initialdir=defaultDirectory, title=title)
    f = open(filePath)
    stockList = f.read().splitlines()
    print(stockList)
    summary = initSummary()
    numStocks = len(stockList)

start = dt.datetime(stYear, stMonth, stDay)
if testNow:
    now = dt.datetime.now()
else:
    now = beforeCovid

yf.pdr_override()

# -------------------------- CALCULATIONS --------------------------

for y in range(len(stockList)):
    buyPrices = []
    buyDates = []

    percentChange = []
    lengthHeld = []
    ticker = stockList[y]
    try:
        data = pdr.get_data_yahoo(ticker, start, now)
    except:
        print("skipped")
        numStocks -= 1
        continue

    if singleTest:
        data["High"].plot(label="high")

    pivotPrices = []
    pivotDates = []
    relevantPivPrices = []
    relevantPivDates = []
    dayCounter = 0
    lastPivot = 0
    lastDate = 0
    rangePrices = []
    rangeDates = []
    for i in range(rangeSize):
        rangePrices.append(0)
        rangeDates.append(0)
    prevPrice = 0

    for i in data.index:
        # Buy
        j = 0
        while j < len(relevantPivDates):
            elapsed = i - relevantPivDates[j]
            if elapsed > dt.timedelta(days=lineRelevanceLength):
                del relevantPivDates[j]
                del relevantPivPrices[j]
            else:
                j += 1
        j = 0
        while j < len(relevantPivDates):
            if prevPrice < relevantPivPrices[j] < data["Adj Close"][i]:
                # BUY!!!
                buyPrices.append(data["Adj Close"][i])
                buyDates.append(i)
                if singleTest:
                    print("Buying at " + str(data["Adj Close"][i]) + " : " + str(i))

                del relevantPivDates[j]
                del relevantPivPrices[j]
            else:
                j += 1

        # Place Pivots
        currentMax = max(rangePrices, default=0)
        value = round(data["High"][i], 3)
        prevPrice = data["Adj Close"][i]

        rangePrices.pop(0)
        rangePrices.append(value)
        rangeDates.pop(0)
        rangeDates.append(i)

        if 0 not in rangePrices[int(rangeSize/2)+1:rangeSize-1]:
            if currentMax == max(rangePrices, default=0):
                dayCounter += 1
            else:
                dayCounter = 0
            if dayCounter == int(rangeSize/2):
                # New Pivot
                lastPivot = currentMax
                pivotPrices.append(currentMax)
                lastDate = rangeDates[int(rangeSize/2)]
                pivotDates.append(rangeDates[int(rangeSize/2)])
                relevantPivPrices.append(currentMax)
                relevantPivDates.append(rangeDates[int(rangeSize/2)])
                # Sell
                j = 0
                while j < len(buyPrices):
                    sellPrice = data["Adj Close"][i]
                    sellDate = i
                    pc = (sellPrice / buyPrices[j] - 1) * 100
                    if pc >= 0 or sellAtLoss:
                        percentChange.append(pc)
                        lengthHeld.append(sellDate - buyDates[j])
                        if singleTest:
                            print("Selling at " + str(sellPrice) + " : " + str(i))
                            print("     % Change: " + str(round(pc, 2)) + "%")
                            print("     Hold Time: " + str(sellDate - buyDates[j]))
                        buyPrices.pop(j)
                        buyDates.pop(j)
                    else:
                        j += 1

        if i == data.index[-1] and len(buyPrices) > 0:
            while len(buyPrices) > 0:
                sellPrice = data["Adj Close"][i]
                sellDate = i
                percentChange.append((sellPrice / buyPrices[0] - 1) * 100)
                lengthHeld.append(sellDate - buyDates[0])
                if singleTest:
                    print("END Selling at " + str(sellPrice) + " : " + str(buyDates[0]))
                    print("     Orig Buy Price: " + str(buyPrices[0]) + " : " + str(i))
                    print("     % Change: " + str(round((sellPrice / buyPrices[0] - 1) * 100, 2)) + "%")
                    print("     Hold Time: " + str(sellDate - buyDates[0]))

                buyPrices.pop(0)
                buyDates.pop(0)

# -------------------------- PRINT --------------------------
    if not len(percentChange) == 0:
        calculateResults(ticker, percentChange, lengthHeld, start, summary, stockList)

    # PLOT
    if singleTest:
        plt.show()

if not singleTest:
    printSummary(summary, numStocks, start)