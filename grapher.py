import pymongo # pymongo to connect to mongoDB
from pymongo import MongoClient

from matplotlib import pyplot as plt # library to graph coin prices over time

import os

# DATABASE CONNECTION
DB_URL = "mongodb+srv://" + str(os.environ.get('PPC_DB_USER')) + ":" + str(os.environ.get('PPC_DB_PASS')) +"@cluster0.omxqk.mongodb.net/btcpricescrapes?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
cluster = MongoClient(DB_URL)
db = cluster["btcpricescrapes"]

# getting scraped data for each of the platforms
bb_entries = [entry for entry in db['bitbuy'].find({})]
ne_entries = [entry for entry in db['newton'].find({})]
cs_entries = [entry for entry in db['coinsmart'].find({})]
sp_entries = [entry for entry in db['shakepay'].find({})]

# plotting for each of the platforms
ne_timestamps = [entry['date'] for entry in ne_entries]
ne_prices = [entry['price'] for entry in ne_entries]
plt.plot(ne_timestamps, ne_prices, label='Newton')

cs_timestamps = [entry['date'] for entry in cs_entries]
cs_prices = [entry['price'] for entry in cs_entries]
plt.plot(cs_timestamps, cs_prices, label='Coinsmart')

sp_timestamps = [entry['date'] for entry in sp_entries]
sp_prices = [entry['price'] for entry in sp_entries]
plt.plot(sp_timestamps, sp_prices, label='Shakepay')

bb_timestamps = [entry['date'] for entry in bb_entries]
bb_prices = [entry['price'] for entry in bb_entries]
plt.plot(bb_timestamps, bb_prices, label='Bitbuy')

plt.xlabel('Timestamps')
plt.ylabel('BTC price-per-coin (CAD)')

plt.legend()

plt.show()
