import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

print(f"{'ID':<4} | {'Price':<6} | {'Source':<30} | {'Name (RU)':<40} | {'Specs'}")
print("-" * 120)
for p in products:
    if "placeholder" in p["image"]:
        name_ru = p.get('name_ru') or ""
        src = p.get('src') or ""
        specs = p.get('specs') or ""
        print(f"{p['id']:<4} | {p['price_cny']:<6} | {src[:30]:<30} | {name_ru[:40]:<40} | {specs}")


