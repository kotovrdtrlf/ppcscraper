
import pymongo # pymongo to connect to mongoDB
from pymongo import MongoClient

from requests_html import HTMLSession # html requests to request and render page
from requests_html import AsyncHTMLSession

import bs4 # bs4 to parse and search html
from bs4 import BeautifulSoup

import datetime as dt # bs4 to parse and search html

import asyncio # asyncio to schedule periodic scraping
import time # to sleep when needed

import os

# DATABASE CONNECTION
DB_URL = "mongodb+srv://" + str(os.environ.get('PPC_DB_USER')) + ":" + str(os.environ.get('PPC_DB_PASS')) +"@cluster0.omxqk.mongodb.net/btcpricescrapes?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
cluster = MongoClient(DB_URL)
db = cluster["btcpricescrapes"]

# function that takes in scraped text and converts it into a float
def formatPrice(scraped_text):
  formatted_price = ""
  for char in scraped_text:
    if char.isnumeric() or char == ".":
      formatted_price += char 
    
  return float(formatted_price)

async def scrapePrice(site_identifier, db_cluster=db):

    # dictionary with str_identfier : link pairs
    web_resources_dict = {
        "bitbuy": "https://bitbuy.ca/en/canadian-cryptocurrency-prices/bitcoin",
        "newton": "https://www.newton.co/prices",
        "coinsmart": "https://www.coinsmart.com/markets/bitcoin/",
        "shakepay": "https://shakepay.com/",
        "kraken": "https://www.kraken.com/prices/xbt-bitcoin-price-chart/cad-canadian-dollar?interval=1m"
    }

    # openning an html session and requesting bitbuy page
    resp = await AsyncHTMLSession().get(web_resources_dict.get(site_identifier))

    # rendering the page to workaround JS affecting DOM
    await resp.html.arender(sleep=1) # delay of 1s to let JS load data

    # get timestamp of scraping
    scrape_timestamp = dt.datetime.now()

    # parsing html
    html = resp.html.html
    soup = bs4.BeautifulSoup(html, "lxml")

    # closing html session
    await resp.session.close()

    try:
        # finding needed html element, if not found - price = "inconclusive"
        if site_identifier == "bitbuy":
            price = soup.findAll('div', {'class':'cell top'})[1].find('b').text

        elif site_identifier == "newton":
            price = soup.find('div',{'class':'grid-text price buy btc'}).text

        elif site_identifier == "coinsmart":
            price = soup.find('div', {'class':'price'}).text

        elif site_identifier == "shakepay":
            price = soup.find('ul', {'class': 'navbar-rates'}).find('li').find('a').text

        # elif site_identifier == "kraken":
            # price = soup.find('div',{'class':'grid-text price buy btc'}).text #Not even going to say anything just look at their HTML
            # price = soup.findAll('a', {'data-testid': 'site-link'})[0].text
        else:
            return 0
        
        # creating entry for database
        scrape_entry = {"date": scrape_timestamp, "price": formatPrice(price)}

        # inserting the entry into database
        db_cluster[site_identifier].insert_one(scrape_entry)

        print(site_identifier + ": " + scrape_timestamp.strftime("%b %d %Y %H:%M:%S") + " = " + str(formatPrice(price)))
    except:
        print(site_identifier + ": " + scrape_timestamp.strftime("%b %d %Y %H:%M:%S") + " = failed to load")

    


""" arguments: number_of_scrapes - number of times to scrape during scraping_time, 1440 times by default
               scraping_time - for how long to scrape in minutes, 1440min(24hrs) by default """
async def startScraping(number_of_scrapes:int=1440, scraping_time:int=1440):

    if (number_of_scrapes > scraping_time):
        # print out error and terminate function
        print("Number of scrape requests cannot be > scraping time")
        print("Max: 1 scrape per 1 minute")
    else:
        # calculate delay between scrapes
        seconds_between_scrapes = (scraping_time / number_of_scrapes) * 60
        print("Will be scraping " + str(number_of_scrapes) + " times ~ every " + str(seconds_between_scrapes) + " second(s)")

        # start the loop ranging in number_of_scrapes
        for _ in range(number_of_scrapes):

            start_time = time.time()
            await asyncio.gather(scrapePrice("bitbuy"),scrapePrice("newton"),scrapePrice("shakepay"),scrapePrice("coinsmart")) # ,scrapePrice("kraken")
            time_spent_scraping =  (round(time.time() - start_time))

            print("Sleeping for " + str(seconds_between_scrapes - time_spent_scraping))
            time.sleep(seconds_between_scrapes - time_spent_scraping)


if __name__ == '__main__':
    print('At this point, needed data has been scraped, scraping disabled')
    
    # preventing accidental script execution as not to damage already scraped data
    """

    # setting up an asycnio event loop to schedule events
    loop = asyncio.get_event_loop()
    task = loop.create_task(startScraping())

    # try starting the loop
    try:
        loop.run_until_complete(task)
        print("Event loop finished, scraping done")
    except asyncio.CancelledError:
        pass

    """

