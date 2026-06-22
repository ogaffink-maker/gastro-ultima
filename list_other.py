import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

others = [p for p in products if p['category'] == 'other']
print(f"Total others: {len(others)}")
for idx, p in enumerate(others[:100]):
    print(f"{p['id']:<4} | {p['price_cny']:<6} | {p['name_ru'][:40]:<40} | {p['name_zh'][:30]:<30} | {p['image']}")
