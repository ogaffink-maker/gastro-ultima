import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('930010单哈萨克斯坦客户报价清单9.30日_raw_pdf.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data:
    if p['page'] == 7:
        print("Page 7 text:")
        print(p['text'])
        print("="*40)
