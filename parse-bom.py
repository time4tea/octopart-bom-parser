import csv
from octopartv3 import Octopart
from decimal import Decimal

def batch_of(data, size=20):
    for i in range(0, len(data), size):
        yield data[i:i + size]


import argparse

parser = argparse.ArgumentParser(description="Parse a BOM and ask octopart for the pricing information")
parser.add_argument("--file", help="file to parse", required=True)
parser.add_argument("--key", help="Octopart API key", required=True)
parser.add_argument("--currency", help="Currency to buy items in", default="GBP")
parser.add_argument("--widgets", type=int, default=1, help="how many widgets you're making")
args = parser.parse_args()

csv_file = open(args.file)

api = Octopart("http://octopart.com/api/v3/", args.key)

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

        best_price = Decimal("Infinity")
        line_price = Decimal(0)
        distributor = "-- Not Found -- "
        product_url = ""

        if result['hits'] > 0:
            for offer in result['items'][0]['offers']:

                if offer['moq'] is None or offer['moq'] < required_quantity:
                    if offer['in_stock_quantity'] > required_quantity:

                        if args.currency not in offer['prices'].keys():
                            continue
                        price = None
                        for price_tuple in offer['prices'][args.currency]:
                            if price_tuple[0] > required_quantity:
                                break
                            price = Decimal(price_tuple[1])

                            if price < best_price:
                                best_price = price
                                line_price = price * required_quantity
                                product_url = offer["product_url"] if offer["product_url"] is not None else "Dunno"
                                distributor = offer["seller"]["name"]

        total_cost += line_price

        print ",".join([
            item["Quantity"],
            item["Part Number"],
            item["Manufacturer"],
            distributor,
            args.currency,
            str(best_price),
            str(line_price),
            product_url
            ])


