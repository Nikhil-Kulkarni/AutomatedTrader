import scraper
from Equity import Equity
from yahoo_finance import Share

equities = scraper.getTodaysEquities()

for equity in equities:
    share = Share(str(equity.ticker))
    print(share.get_price())

# Implement trading strategy here
# Strategy Idea 1:
# 1. Buy the stock with the most common buy rating
# 2. Sell entire portfolio the next morning and repeat


#Strategy Idea 2:
# 1.
