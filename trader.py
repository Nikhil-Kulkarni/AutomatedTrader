import scraper
from Equity import Equity
from DecimalEncoder import DecimalEncoder
from datetime import date
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from googlefinance import getQuotes
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
def trade(money):
    equities = scraper.getTodaysEquities()
    equitiesBuyRating = []
    stocks = dynamodb.Table('Stocks')

    for equity in equities:
        if str(equity.currentRating) == " Buy":
            equitiesBuyRating.append(str(equity.ticker))

    # Most common BUY Rating
    mostCommonBuyTicker = max(set(equitiesBuyRating), key=equitiesBuyRating.count)
    priceOfShare = getQuotes(mostCommonBuyTicker)[0]['LastTradePrice']

    # Compute the number of shares I can buy
    numberOfShares = math.floor(money/priceOfShare)

    # Timestamp
    today = date.today()
    timestamp = str(today.year) + "-" + str(today.month) + "-" + str(today.day)

    # Save to db
    response = stocks.put_item(
        Item={
            'ticker':mostCommonBuyTicker,
            'timestamp':timestamp,
            'price':decimal.Decimal(str(priceOfShare)),
            'shares':decimal.Decimal(numberOfShares),
            'transactionType':'BUY'
        }
    )

# Sell entire portfolio
def sell():
    stocks = dynamodb.Table('Stocks')

    today = date.today()
    timestamp = str(today.year) + "-" + str(today.month) + "-" + str(today.day)


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
        item = response['Item']

        numberShares = item['shares']
        lastTradePrice = getQuotes(str(item['ticker']))[0][u'LastTradePrice']

        amountIMade = float(lastTradePrice) * float(numberShares) - float(item['price']) * float(numberShares)
        print(amountIMade)

        # Save to db
        response = stocks.put_item(
            Item={
                'ticker':str(item['ticker']),
                'timestamp':timestamp,
                'price':decimal.Decimal(str(lastTradePrice)),
                'shares':decimal.Decimal(numberShares),
                'transactionType':'SELL'
            }
        )

        # trade(amountIMade)



# Trade
sell()
