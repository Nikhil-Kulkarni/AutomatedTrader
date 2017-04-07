import urllib2
from datetime import date
from bs4 import BeautifulSoup
from Equity import Equity

# Get today's upgrades
def getTodaysEquities(currentDate):
    today = currentDate
    content = urllib2.urlopen("https://www.briefing.com/Investor/Calendars/Upgrades-Downgrades/Upgrades/" + str(today.year) + "/" + str(today.month) + "/" + str(today.day)).read()

    soup = BeautifulSoup(content, "html5lib")
    # Find all equities
    upgrades = soup.find_all("tr", {"class" : ["wh-row", "hl-row"]})

    # List of equities that have changed analyst ratings
    equities = []

    for equity in upgrades:
        equityInfo = equity.find_all("td")
        name = equityInfo[0].text
        ticker = equityInfo[1].text
        brokerage = equityInfo[2].text
        ratingChange = equityInfo[3].text.split(u"\u00BB")
        previousRating = ratingChange[0]
        currentRating = ratingChange[1]

        # Append Equity to object to array
        equities.append(Equity(name, ticker, brokerage, previousRating, currentRating))

    return equities
