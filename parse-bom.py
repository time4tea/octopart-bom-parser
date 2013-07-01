import csv
import money
from octopartv3 import Octopart
from decimal import Decimal


def batch_of(data, size=20):
    for i in range(0, len(data), size):
        yield data[i:i + size]


class StringMatch:

    def __init__(self, s):
        self._s = s

    def matches(self, s):
        return self._s == s


class AnyMatch:

    def matches(self,s):
        return True


class InMatch:

    def __init__(self, l):
        self._l = l

    def matches(self, i):
        return i in self._l


class Price:

    def __init__(self, money, distributor, url):
        self._money = money
        self._distributor = distributor
        self._url = url

    def __str__(self):
        return "Price: " + str(self._money) + " Dist: " + self._distributor + " URL:" + self._url

import argparse

parser = argparse.ArgumentParser(description="Parse a BOM and ask octopart for the pricing information")
parser.add_argument("--file", help="file to parse", required=True)
parser.add_argument("--key", help="Octopart API key", required=True)
parser.add_argument("--currency", help="Preferred currency to buy items in", default="GBP")
parser.add_argument("--dist", help="Limit to a distributor", action="append")
parser.add_argument("--widgets", type=int, default=1, help="how many widgets you're making")
args = parser.parse_args()

csv_file = open(args.file)

api = Octopart("http://octopart.com/api/v3/", args.key)

required_distributor = InMatch(args.dist) if args.dist is not None else AnyMatch()

csv_reader = csv.DictReader(csv_file)
line_items = []
queries = []
for line_item in csv_reader:
    if not line_item['Part Number'] or not line_item['Manufacturer']:
        continue
    line_items.append(line_item)

results = []

for batch in batch_of(line_items):
    match = api.partsmatch()

    items = list(batch)

    for (idx, item) in enumerate(items):
        match.query_mpn(item["Part Number"], item["Manufacturer"], idx)

    results = match.execute()

    total_cost = Decimal(0)

    for result in results["results"]:

        item = items[result['reference']]
        required_quantity = int(item["Quantity"]) * args.widgets

        valid_prices = []

        if result['hits'] > 0:
            for offer in result['items'][0]['offers']:
                if offer['moq'] is None or offer['moq'] < required_quantity:
                    if offer['in_stock_quantity'] > required_quantity:

                        prices = offer['prices']

                        for currency in prices.keys():
                            price = None
                            for price_tuple in prices[currency]:
                                if price_tuple[0] > required_quantity:
                                    break
                                price = Price(
                                    money.Money(price_tuple[1], currency),
                                    offer["seller"]["name"],
                                    offer["product_url"]
                                )
                            if price is not None:
                                valid_prices.append(price)

        for price in valid_prices:
            print price

        #line_price = best_price * required_quantity
        #total_cost += line_price

        #print ",".join([
        #    item["Quantity"],
        #    item["Part Number"],
        #    item["Manufacturer"],
        #    distributor,
        #    args.currency,
        #    str(best_price),
        #    str(line_price),
        #    product_url
        #    ])


