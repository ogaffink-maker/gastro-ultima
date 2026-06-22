import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('2026.5.21（中汇）xlsx_raw_pdf.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data:
    if 'Ice maker' in p['text']:
        print(f"Page {p['page']}:")
        print(p['text'])
        print("="*40)
