import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr

def initSummary():
    empty = {'Average Number of Trades': [0],
             'Average Gain Hold Time': [dt.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)],
             'Average Loss Hold Time': [dt.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)],
             'Average Hold Time': [dt.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)],
             'Average Winrate': [0],
             'Average Gain/Loss Ratio': [0],
             'Average Gain': [0],
             'Average Loss': [0],
             'Average % Change': [0],
             'Average Max Gain': [0],
             'Average Max Loss': [0],
             'Average % Change * Number of Trades': [0],
             'Average Simulated Return': [0]}
    return pd.DataFrame(empty, ['Average Number of Trades',
                                'Average Gain Hold Time',
                                'Average Loss Hold Time',
                                'Average Hold Time',
                                'Average Winrate',
                                'Average Gain/Loss Ratio',
                                'Average Gain',
                                'Average Loss',
                                'Average % Change',
                                'Average Max Gain',
                                'Average Max Loss',
                                'Average % Change * Number of Trades',
                                'Average Simulated Return'])


def calculateResults(ticker, percentChange, lengthHeld, start, summary, stockList=None):
    gainsHoldTime = dt.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    lossHoldTime = dt.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    holdTime = dt.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

    gains = 0
    numGains = 0
    losses = 0
    numLosses = 0
    totalReturn = 1
    averageChange = 0

    ii = 0
    for i in percentChange:
        if i > 0:
            gains += i
            numGains += 1
            gainsHoldTime += lengthHeld[ii]
        else:
            losses += i
            numLosses += 1
            lossHoldTime += lengthHeld[ii]
        totalReturn = totalReturn * ((i / 100) + 1)
        holdTime += lengthHeld[ii]
        averageChange += i
        ii += 1

    totalReturn = round((totalReturn - 1) * 100, 2)
    averageChange /= len(percentChange)

    if numGains > 0:
        avgGain = gains / numGains
        maxReturn = str(max(percentChange))
    else:
        avgGain = 0
        maxReturn = "undefined"

    if numLosses > 0:
        avgLoss = losses / numLosses
        maxLoss = str(min(percentChange))
        if avgLoss == 0:
            avgLoss = 0.00000001
        ratio = -avgGain / avgLoss
    else:
        avgLoss = 0
        maxLoss = "undefined"
        ratio = "inf"

    if numGains > 0 or numLosses > 0:
        winrate = (numGains / (numGains + numLosses))*100
    else:
        winrate = 0

    # ------------- Update summary -------------
    if not isinstance(summary, int):
        summary['Average Number of Trades'][0] += len(percentChange)
        if numGains > 0:
            summary['Average Gain Hold Time'][0] += gainsHoldTime/numGains
        if numLosses > 0:
            summary['Average Loss Hold Time'][0] += lossHoldTime/numLosses
        summary['Average Hold Time'][0] += holdTime/len(percentChange)
        summary['Average Winrate'][0] += winrate
        # summary['Average Gain/Loss Ratio'][0] += ratio
        summary['Average Gain'][0] += avgGain
        summary['Average Loss'][0] += avgLoss
        summary['Average % Change'][0] += averageChange
        summary['Average Max Gain'][0] += max(percentChange)
        summary['Average Max Loss'][0] += min(percentChange)
        summary['Average % Change * Number of Trades'][0] += averageChange * len(percentChange)
        summary['Average Simulated Return'][0] += totalReturn

    # ------------- Print Results -------------
    if stockList == None or len(stockList) <= 10:
        print()
        print("Results for " + ticker + " going back to " + str(start) +
              ", Sample size: " + str(numGains + numLosses) + " trades")
        if numGains > 0:
            print("Average Gain Hold Time: " + str(gainsHoldTime/numGains))
        if numLosses > 0:
            print("Average Loss Hold Time: " + str(lossHoldTime/numLosses))
        print("Average Hold Time: " + str(holdTime/len(percentChange)))
        print("Winrate: " + str(round(winrate, 3)) + "%")
        print("Gain/loss ratio: " + str(ratio))
        print("Average Gain: " + str(round(avgGain, 3)) + "%")
        print("Average Loss: " + str(round(avgLoss, 3)) + "%")
        print("Average % Change: " + str(round(averageChange, 3)) + "%")
        print("Max Return: " + maxReturn + "%")
        print("Max Loss: " + maxLoss + "%")
        print("Average % Change * Number of Trades: " + str(round(averageChange * len(percentChange), 3)) + "%")
        print("Simulated return over " + str(numGains + numLosses) +
              " trades: " + str(totalReturn) + "%")
        print()


def printSummary(summary, numStocks, start):
    print("\n---------------------- RESULTS SUMMARY ----------------------\n")
    print("Results for " + str(numStocks) + " stocks, starting " + str(start) +
          ", Sample size: " + str(summary['Average Number of Trades'][0]) + " total trades")
    print("Average Number of Trades Per Stock: " + str(summary['Average Number of Trades'][0]/numStocks))
    print("Average of Average Gain Hold Times: " + str(summary['Average Gain Hold Time'][0]/numStocks))
    print("Average of Average Loss Hold Times: " + str(summary['Average Loss Hold Time'][0]/numStocks))
    print("Average of Average Hold Times: " + str(summary['Average Hold Time'][0]/numStocks))
    print("Average Winrate: " + str(round(summary['Average Winrate'][0]/numStocks, 3)) + "%")
    # print("Average Gain/loss ratio: " + str(summary['Average Gain/Loss Ratio'][0]/numStocks))
    print("Average of Average Gains: " + str(round(summary['Average Gain'][0]/numStocks, 3)) + "%")
    print("Average of Average Losses: " + str(round(summary['Average Loss'][0]/numStocks, 3)) + "%")
    print("Average of Average % Changes: " + str(round(summary['Average % Change'][0]/numStocks, 3)) + "%")
    print("Average Max Return: " + str(round(summary['Average Max Gain'][0]/numStocks, 3)) + "%")
    print("Average Max Loss: " + str(round(summary['Average Max Loss'][0]/numStocks, 3)) + "%")
    print("Average of Average % Changes * Number of Trades: " +
          str(round(summary['Average % Change * Number of Trades'][0]/numStocks, 3)) + "%")
    print("Average Simulated return: " + str(round(summary['Average Simulated Return'][0]/numStocks, 3)) + "%")