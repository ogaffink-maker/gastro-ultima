import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

workspace = r"c:\Users\Auditore\Downloads\price list"

# Load the raw parsed files
raw_excel_files = [f for f in os.listdir(workspace) if f.endswith('_raw.json')]
raw_pdf_files = [f for f in os.listdir(workspace) if f.endswith('_raw_pdf.json')]

with open(os.path.join(workspace, "products.json"), "r", encoding="utf-8") as f:
    products = json.load(f)

print(f"{'ID':<4} | {'Price':<6} | {'Found in File':<50} | {'Details'}")
print("-" * 120)

for p in products:
    if "placeholder" in p["image"]:
        name_ru = p.get('name_ru', '')
        name_zh = p.get('name_zh', '')
        price_cny = p.get('price_cny')
        
        # We will search by:
        # 1. Matching price_cny AND (some words from name_ru OR name_zh)
        # 2. Or matching a unique ID or name_zh substring if present
        ru_words = [w.lower() for w in re.findall(r"\b\w{3,}\b", name_ru) if w.lower() not in ['machine', 'steel', 'aluminum', 'soup', 'with', 'style', 'head']]
        zh_sub = name_zh.strip()
        
        found = False
        # Search in excel files first
        for ef in raw_excel_files:
            ef_path = os.path.join(workspace, ef)
            with open(ef_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for sheetname, rows in data.items():
                for idx, r in enumerate(rows):
                    if r and len(r) > 2:
                        # check price and text matching
                        r_price = 0.0
                        if sheetname == 'Оборудование' and 'Жантуре' in ef:
                            r_price = r[6] if len(r) > 6 else 0.0
                        elif sheetname == 'Посуда' and 'Жантуре' in ef:
                            r_price = r[4] if len(r) > 4 else 0.0
                        else:
                            r_price = r[6] if len(r) > 6 else 0.0
                            
                        try:
                            r_price = float(str(r_price).replace(',', '').strip()) if r_price is not None else 0.0
                        except ValueError:
                            r_price = 0.0
                            
                        r_text = " ".join([str(x) for x in r if x is not None]).lower()
                        
                        price_match = (abs(r_price - price_cny) < 0.01) if price_cny else True
                        text_match = False
                        if zh_sub and zh_sub.lower() in r_text:
                            text_match = True
                        elif ru_words and any(w in r_text for w in ru_words):
                            text_match = True
                            
                        if price_match and text_match:
                            print(f"{p['id']:<4} | {p['price_cny']:<6} | {ef[:-9]:<50} | Sheet: {sheetname}, Row: {idx+1} | Raw: {r_text[:40]}")
                            found = True
                            break
                if found:
                    break
            if found:
                continue
                
        # Search in pdf files
        for pf in raw_pdf_files:
            pf_path = os.path.join(workspace, pf)
            with open(pf_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for page_idx, page_data in enumerate(data):
                text = page_data['text']
                
                # Check text for words and price
                price_str = str(int(price_cny)) if price_cny else ""
                price_match = (price_str in text) if price_str else True
                
                text_match = False
                if zh_sub and zh_sub in text:
                    text_match = True
                elif ru_words and any(w in text.lower() for w in ru_words):
                    text_match = True
                    
                if price_match and text_match:
                    # Find matching line or paragraph in text
                    lines = text.split('\n')
                    matching_line = ""
                    for line in lines:
                        if (zh_sub and zh_sub in line) or (ru_words and any(w in line.lower() for w in ru_words)):
                            matching_line = line.strip()
                            break
                    print(f"{p['id']:<4} | {p['price_cny']:<6} | {pf[:-13]:<50} | Page: {page_data['page']} | Line: {matching_line[:40]}")
                    found = True
                    break
            if found:
                continue
                
        if not found:
            print(f"{p['id']:<4} | {p['price_cny']:<6} | NOT FOUND ANYWHERE! | Name_ru: {name_ru}, Name_zh: {name_zh}")

