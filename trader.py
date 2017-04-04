import scraper
from Equity import Equity
from yahoo_finance import Share

equities = scraper.getTodaysEquities()

for equity in equities:
    share = Share(str(equity.ticker))
    print(share.get_price())

# Implement trading strategy here
