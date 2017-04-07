import scraper
from Equity import Equity
from DecimalEncoder import DecimalEncoder
from datetime import date
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from googlefinance import getQuotes
from yahoo_finance import Share
import boto3
import math
import decimal
import json

# Save today's buys and sells
dynamodb = boto3.resource('dynamodb')

# Implement trading strategy here
# Strategy Idea 1:
# 1. Buy the stock with the most common buy rating
# 2. Sell entire portfolio the next morning and repeat
def trade(money, currentDate):
    equities = scraper.getTodaysEquities(currentDate)
    equitiesBuyRating = []
    stocks = dynamodb.Table('Stocks')

    for equity in equities:
        if str(equity.currentRating) == " Strong Buy" or str(equity.currentRating) == " Outperform" or str(equity.currentRating) == " Sector Outperform" or str(equity.currentRating) == " Mkt Outperform":
            equitiesBuyRating.append(equity)

    listOfPurchases = []
    topStocksToPurchase = equitiesBuyRating[:4]

    # Take 4 4 stocks and buy them
    for stock in topStocksToPurchase:
        amountInvestedPerStock = float(money / len(topStocksToPurchase))

        ticker = stock.ticker
        share = Share(str(ticker))
        priceOfShare = float(share.get_historical(str(currentDate), str(currentDate))[0]['Open'])

        # Compute the number of shares of this stock I can buy
        numberOfShares = math.floor(amountInvestedPerStock/priceOfShare)
        listOfPurchases.append({'price':decimal.Decimal(str(priceOfShare)), 'shares':decimal.Decimal(str(numberOfShares)), 'ticker':str(ticker)})

    # Buy the shares and save to DB
    timestamp = str(currentDate.year) + "-" + str(currentDate.month) + "-" + str(currentDate.day)

    # Save to db
    response = stocks.put_item(
        Item={
            'transactionType':'BUY',
            'timestamp':timestamp,
            'listOfPurchases':listOfPurchases,
            'bank':decimal.Decimal(str(money))
        }
    )

# Sell entire portfolio
def sell(currentDate):
    stocks = dynamodb.Table('Stocks')

    today = currentDate
    timestamp = str(today.year) + "-" + str(today.month) + "-" + str(today.day - 1)

    # January
    # if (currentDate.day in [9, 16, 23, 30]):
    # February/March:
    if (currentDate.day in [6, 13, 20, 27]):
        timestamp = str(today.year) + "-" + str(today.month) + "-" + str(today.day - 3)

    # January
    # if (currentDate.day in [17]):
    # February:
    # if (currentDate.day in [21]):
    #     timestamp = str(today.year) + "-" + str(today.month) + "-" + str(today.day - 4)

    try:
        response = stocks.get_item(
            Key={
                'timestamp': timestamp,
                'transactionType':'BUY'
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        purchase = response['Item']
        itemsPurchased = purchase['listOfPurchases']

        portfolioValue = 0
        amountNotInvested = 0
        listOfSells = []

        for item in itemsPurchased:
            numberShares = item['shares']
            ticker = item['ticker']
            share = Share(str(item['ticker']))
            lastTradePrice = float(share.get_historical(str(currentDate), str(currentDate))[0]['Open'])
            portfolioValue = portfolioValue + float(lastTradePrice) * float(numberShares)
            amountNotInvested = amountNotInvested + (float(purchase['bank']/len(itemsPurchased)) - float(numberShares) * float(item['price']))
            listOfSells.append({'price':decimal.Decimal(str(lastTradePrice)), 'shares':decimal.Decimal(str(numberShares)), 'ticker':str(ticker)})

        newBankValue = portfolioValue + amountNotInvested
        print("Net gain: " + str(newBankValue - float(purchase['bank'])))
        print("Bank: " + str(newBankValue))

        # Timestamp
        today = currentDate
        timestamp = str(today.year) + "-" + str(today.month) + "-" + str(today.day)

        # Save to db
        response = stocks.put_item(
            Item={
                'transactionType':'BUY',
                'timestamp':timestamp,
                'listOfPurchases':listOfSells,
                'bank':decimal.Decimal(str(newBankValue))
            }
        )

        trade(newBankValue, currentDate)

# Strategy Idea 2:
# 1. Choose 4 stocks with strong buy or outperform rating
# and buy equal amounts of all 4
# 2. Sell the next morning and repeat

# Trade - January
# initialDate = date(2017, 1, 3)
# initialBank = 3000
# trade(initialBank, initialDate)
# for day in range(4, 32) :
#     if day not in [7, 8, 14, 15, 16, 21, 22, 28, 29]:
#         currentDate = date(2017, 1, day)
#         sell(currentDate)

# Trade - February
# initialDate = date(2017, 2, 1)
# initialBank = 3655.879601
# trade(initialBank, initialDate)
# for day in range(2, 29) :
#     if day not in [4, 5, 11, 12, 18, 19, 20, 25, 26]:
#         currentDate = date(2017, 2, day)
#         sell(currentDate)

# # Trade - March
initialDate = date(2017, 3, 1)
initialBank = 1000
trade(initialBank, initialDate)
# sell(initialDate)
for day in range(2, 32) :
    if day not in [4, 5, 11, 12, 18, 19, 25, 26]:
        currentDate = date(2017, 3, day)
        sell(currentDate)
