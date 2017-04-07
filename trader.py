import scraper
from Equity import Equity
from DecimalEncoder import DecimalEncoder
from yahoo_finance import Share
from datetime import date
import boto3
import math
import decimal

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
    share = Share(mostCommonBuyTicker)
    priceOfShare = float(share.get_price())

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

# Trade
trade(1000)
