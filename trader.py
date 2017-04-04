import scraper
from Equity import Equity

equities = scraper.getTodaysEquities()

for equity in equities:
    print(equity.name)

# Implement trading strategy here
