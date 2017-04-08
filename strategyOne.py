import scraper
from Equity import Equity
from DecimalEncoder import DecimalEncoder
from datetime import timedelta, date
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from googlefinance import getQuotes
from yahoo_finance import Share, YQLResponseMalformedError
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
class Trader(object):

    def __init__(self):
        self.deltaDays = 0

    def trade(self, money, currentDate):
        equities = scraper.getTodaysEquities(currentDate)
        equitiesBuyRating = []
        stocks = dynamodb.Table('Stocks')

        for equity in equities:
            if str(equity.currentRating) == " Strong Buy" or str(equity.currentRating) == " Outperform" or str(equity.currentRating) == " Sector Outperform" or str(equity.currentRating) == " Mkt Outperform":
                equitiesBuyRating.append(str(equity.ticker))

        # Most common BUY Rating
        if len(equitiesBuyRating) != 0:
            try:
                mostCommonBuyTicker = max(set(equitiesBuyRating), key=equitiesBuyRating.count)
                # priceOfShare = float(getQuotes(mostCommonBuyTicker)[0]['LastTradePrice'])
                share = Share(str(mostCommonBuyTicker))
                priceOfShare = float(share.get_historical(str(currentDate), str(currentDate))[0]['Open'])

                # Compute the number of shares I can buy
                numberOfShares = math.floor(money/priceOfShare)

                # Timestamp
                today = currentDate
                timestamp = str(today.year) + "-" + str(today.month) + "-" + str(today.day)

                # Save to db
                response = stocks.put_item(
                    Item={
                        'ticker':mostCommonBuyTicker,
                        'timestamp':timestamp,
                        'price':decimal.Decimal(str(priceOfShare)),
                        'shares':decimal.Decimal(numberOfShares),
                        'transactionType':'BUY',
                        'bank':decimal.Decimal(str(money))
                    }
                )
                self.deltaDays = 0
            except Exception as e:
                # print e
                self.deltaDays = self.deltaDays + 1
        else:
            self.deltaDays = self.deltaDays + 1

    # Sell entire portfolio
    def sell(self, currentDate):
        stocks = dynamodb.Table('Stocks')

        today = currentDate - timedelta(days=(1+self.deltaDays))
        timestamp = str(today.year) + "-" + str(today.month) + "-" + str(today.day)

        if (currentDate.weekday() == 0):
            today = currentDate - timedelta(days=(3+self.deltaDays))
            timestamp = str(today.year) + "-" + str(today.month) + "-" + str(today.day)

        # print timestamp

        try:
            response = stocks.get_item(
                Key={
                    'timestamp': timestamp,
                    'transactionType':'BUY'
                }
            )
        except ClientError as e:
            # print(e.response['Error']['Message'])
            test = 'hello'
        else:
            # print currentDate
            # print timestamp
            item = response['Item']


            numberShares = item['shares']
            # lastTradePrice = getQuotes(str(item['ticker']))[0][u'LastTradePrice']
            share = Share(str(item['ticker']))

            try:
                lastTradePrice = float(share.get_historical(str(currentDate), str(currentDate))[0]['Open'])
            except YQLResponseMalformedError as e:
                if (currentDate.weekday() == 0):
                    self.deltaDays = self.deltaDays + 3
                else:
                    self.deltaDays = self.deltaDays + 1
                return

            lastTradePrice = float(share.get_historical(str(currentDate), str(currentDate))[0]['Open'])

            amountIMade = float(lastTradePrice) * float(numberShares) - float(item['price']) * float(numberShares)
            # print("Net gain: " + str(amountIMade))
            valueInBank = float(lastTradePrice) * float(numberShares) + (float(item['bank']) - float(numberShares) * float(item['price']))
            print(str(valueInBank))

            # Timestamp
            today = currentDate
            timestamp = str(today.year) + "-" + str(today.month) + "-" + str(today.day)

            # Save to db
            response = stocks.put_item(
                Item={
                    'ticker':str(item['ticker']),
                    'timestamp':timestamp,
                    'price':decimal.Decimal(str(lastTradePrice)),
                    'shares':decimal.Decimal(numberShares),
                    'transactionType':'SELL',
                    'bank':decimal.Decimal(str(valueInBank))
                }
            )

            self.trade(valueInBank, currentDate)

# Trade - January
# initialDate = date(2017, 1, 3)
# initialBank = 1000
# trade(initialBank, initialDate)
# for day in range(4, 32) :
#     if day not in [7, 8, 14, 15, 16, 21, 22, 28, 29]:
#         currentDate = date(2017, 1, day)
#         sell(currentDate)

# Trade - February
# initialDate = date(2017, 2, 1)
# initialBank = 1000
# trade(initialBank, initialDate)
# for day in range(2, 29) :
#     if day not in [4, 5, 11, 12, 18, 19, 20, 25, 26]:
#         currentDate = date(2017, 2, day)
#         sell(currentDate)

# Trade - March
# initialDate = date(2017, 3, 1)
# initialBank = 75000
# trade(initialBank, initialDate)
# for day in range(2, 32) :
#     if day not in [4, 5, 11, 12, 18, 19, 25, 26]:
#         currentDate = date(2017, 3, day)
#         sell(currentDate)


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

trader = Trader()

start = date(2016, 4, 8)
trader.trade(3000, start)
start_date = date(2016, 4, 9)
end_date = date(2017, 4, 6)
for single_date in daterange(start_date, end_date):
    if single_date.weekday() < 5:
        # print single_date.strftime("%Y-%m-%d")
        trader.sell(single_date)
