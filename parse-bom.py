import csv
from octopartv3 import Octopart


def batch_of(data, size=20):
    for i in range(0, len(data), size):
        yield data[i:i + size]


import argparse

parser = argparse.ArgumentParser(description="Parse a BOM and ask octopart for the pricing information")
parser.add_argument("--file", help="file to parse", required=True)
parser.add_argument("--key", help="Octopart API key", required=True)
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

    for result in results:

        item = items[result['reference']]
        required_quantity = item["Quantity"] * args.widgets

        for offer in result['items'][0]['offers']:
            if 'USD' not in offer['prices'].keys():
                continue
            price = None
            for price_tuple in offer['prices']['USD']:
                # Find correct price break
                if price_tuple[0] > quantity:
                    break
                    # Cast pricing string to Decimal for precision
                # calculations
                price = Decimal(price_tuple[1])
            if price is not None:
                prices.append(price)


    print result
