import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

print(f"{'ID':<4} | {'Price':<6} | {'Name (RU)':<50} | {'Name (ZH)':<30}")
print("-" * 100)

eng_count = 0
for p in products:
    name_ru = p.get('name_ru', '')
    # Check if name is mostly English
    if re.search(r"[a-zA-Z]", name_ru) and not re.search(r"[а-яА-ЯёЁ]", name_ru):
        print(f"{p['id']:<4} | {p['price_cny']:<6} | {p['name_ru'][:50]:<50} | {p['name_zh'][:30]:<30}")
        eng_count += 1

print(f"Total English products: {eng_count}")
