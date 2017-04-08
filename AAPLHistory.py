from yahoo_finance import Share
import boto3
import decimal
from boto3.dynamodb.conditions import Key, Attr
from DecimalEncoder import DecimalEncoder


dynamodb = boto3.resource('dynamodb')
ticker = 'AAPL'
share = Share(ticker)
historicalData = share.get_historical('2002-1-1', '2017-4-7')

AAPLHistory = dynamodb.Table('AAPLHistory')

for data in historicalData:
    Volume = float(data['Volume'])
    Symbol = data['Symbol']
    Adj_Close = float(data['Adj_Close'])
    High = float(data['High'])
    Low = float(data['Low'])
    Date = data['Date']
    Close = float(data['Close'])
    Open = float(data['Open'])

    response = AAPLHistory.put_item(
        Item={
            'timestamp':str(Date),
            'Volume':decimal.Decimal(str(Volume)),
            'Symbol':str(Symbol),
            'Adj_Close':decimal.Decimal(str(Adj_Close)),
            'High':decimal.Decimal(str(High)),
            'Low':decimal.Decimal(str(Low)),
            'Close':decimal.Decimal(str(Close)),
            'Open':decimal.Decimal(str(Open))
        }
    )
