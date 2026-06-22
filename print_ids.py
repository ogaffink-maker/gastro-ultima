import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

for x in products[319:]:
    print(f"ID: {x['id']:<4} | Price: {x['price_cny']:<6} | RU: {x['name_ru'][:50]:<50} | ZH: {x['name_zh']}")

