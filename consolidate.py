import os
import sys
import json
import re
import shutil
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

workspace = r"c:\Users\Auditore\Downloads\price list"
img_dir = os.path.join(workspace, "extracted_images")
dest_img_dir = os.path.join(workspace, "images")
os.makedirs(dest_img_dir, exist_ok=True)

print("Starting consolidation process...")

# Helper to convert JP2 to JPG
def convert_jp2_to_jpg(path):
    if not os.path.exists(path):
        return None
    try:
        base, ext = os.path.splitext(path)
        if ext.lower() in ['.jp2', '.jpx']:
            jpg_path = base + ".jpg"
            with Image.open(path) as img:
                img.convert("RGB").save(jpg_path, "JPEG")
            os.remove(path)
            return jpg_path
    except Exception as e:
        # print(f"  Error converting JP2 {path}: {e}")
        pass
    return path

# 1. Convert all JP2 files in the images folder
print("Converting JP2 images to standard JPEGs for browser compatibility...")
for root, dirs, files in os.walk(img_dir):
    for f in files:
        if f.lower().endswith('.jp2'):
            convert_jp2_to_jpg(os.path.join(root, f))

# Set of all products collected
all_raw_products = []

# Helper to clean and split name into Chinese and Russian/English
def split_name(name_str):
    if not name_str:
        return "", ""
    lines = [l.strip() for l in name_str.split('\n') if l.strip()]
    zh_lines = []
    ru_lines = []
    for l in lines:
        if re.search(r"[\u4e00-\u9fa5]", l):
            zh_lines.append(l)
        else:
            ru_lines.append(l)
    
    zh_name = " ".join(zh_lines).strip()
    ru_name = " ".join(ru_lines).strip()
    
    # fallback if name was all Chinese or all Russian
    if not zh_name and ru_name:
        # Check if there is Chinese in it anyway
        if re.search(r"[\u4e00-\u9fa5]", name_str):
            zh_name = name_str
            ru_name = ""
    elif not ru_name and zh_name:
        # check if there are English letters/Cyrillic
        if re.search(r"[a-zA-Zа-яА-ЯёЁ]", name_str):
            ru_name = name_str
            zh_name = ""
            
    return zh_name, ru_name

# Helper to normalize sizes
def clean_size(size_val):
    if size_val is None:
        return ""
    size_str = str(size_val).strip()
    size_str = re.sub(r"\s+", " ", size_str)
    return size_str

# Helper to clean specs
def clean_specs(specs_val):
    if specs_val is None:
        return ""
    specs_str = str(specs_val).strip()
    specs_str = re.sub(r"\s+", " ", specs_str)
    return specs_str

# Helper to map images from Excel files
def find_xlsx_image(filename, sheetname, row_num):
    clean_fn = filename.replace('.xlsx', '').replace(' ', '_')
    # Look for files matching pattern: xlsx_<clean_fn>_<sheetname>_row<row_num>_col*
    # inside img_dir
    if not os.path.exists(img_dir):
        return None
    for f in os.listdir(img_dir):
        if f.startswith(f"xlsx_{clean_fn}_{sheetname}_row{row_num}_col"):
            return os.path.join(img_dir, f)
    return None

# ==========================================
# PART 2: Parse Excel files
# ==========================================
print("\n--- Parsing Excel files ---")
xlsx_files = [f for f in os.listdir(workspace) if f.endswith('.xlsx')]

for f in xlsx_files:
    raw_json_path = os.path.join(workspace, f.replace(".xlsx", "_raw.json"))
    if not os.path.exists(raw_json_path):
        continue
    
    print(f"Processing Excel raw JSON: {f}")
    with open(raw_json_path, 'r', encoding='utf-8') as jf:
        data = json.load(jf)
    
    for sheetname, rows in data.items():
        if sheetname == 'Лист1' and f.startswith('Айдос'):
            continue # Skip summary sheet
        
        # Detect headers
        header_idx = -1
        for idx, r in enumerate(rows):
            if r and any(isinstance(x, str) and ('序号' in x or 'No' in x or '商品名称' in x or 'Product' in x or 'Название' in x) for x in r):
                header_idx = idx
                break
        
        if header_idx == -1:
            header_idx = 0 # Default to 0 if not found
            
        print(f"  Sheet: {sheetname}, header at row {header_idx+1}")
        
        # Parse data rows
        for r_idx in range(header_idx + 1, len(rows)):
            row_val = rows[r_idx]
            if not row_val or not any(x is not None for x in row_val):
                continue
            
            # Map columns based on sheet name and structure
            # Default columns:
            seq = row_val[0]
            name = None
            size = ""
            unit = "PCS"
            qty = 1
            price_cny = 0.0
            specs = ""
            
            if sheetname == 'Оборудование' and 'Жантуре' in f:
                # Columns: [0: seq, 1: img, 2: name/desc, 3: size, 4: unit, 5: qty, 6: price, 7: total, 8: specs]
                name = row_val[2]
                size = row_val[3]
                unit = row_val[4] if len(row_val) > 4 and row_val[4] else "台"
                qty = row_val[5] if len(row_val) > 5 and row_val[5] else 1
                price_cny = row_val[6] if len(row_val) > 6 and row_val[6] else 0.0
                specs = row_val[8] if len(row_val) > 8 and row_val[8] else ""
            elif sheetname == 'Посуда' and 'Жантуре' in f:
                # Columns: [0: img, 1: code, 2: name, 3: qty, 4: price, 5: total, 6: size]
                # Row 5 was headers: ['Фото', 'Номер', 'Название', 'Количество', 'Цена', 'Общая цена', 'Размеры']
                if r_idx < 5: # skip header rows
                    continue
                name = row_val[2]
                size = row_val[6] if len(row_val) > 6 else ""
                qty = row_val[3] if len(row_val) > 3 else 1
                price_cny = row_val[4] if len(row_val) > 4 else 0.0
                unit = "PCS"
                specs = f"Код: {row_val[1]}" if len(row_val) > 1 and row_val[1] else ""
            else:
                # Standard sheets like 哈萨克斯坦2, 哈萨克斯坦2(1), 哈萨克斯坦客户报价清单8.8
                # Columns: [seq, img, name, size, unit, qty, price, total, remarks/specs]
                name = row_val[2] if len(row_val) > 2 else None
                size = row_val[3] if len(row_val) > 3 else ""
                unit = row_val[4] if len(row_val) > 4 else "PCS"
                qty = row_val[5] if len(row_val) > 5 else 1
                price_cny = row_val[6] if len(row_val) > 6 else 0.0
                specs = row_val[8] if len(row_val) > 8 else ""
            
            if not name or not str(name).strip():
                continue
            
            name_str = str(name).strip()
            # Skip totals and metadata rows
            if any(h in name_str for h in ['合计', 'Total', '单号', '收货', 'Buyer', 'Date', '微信', '支付宝', '购买须知', '此报价', '付款方式', '定金', '余款']):
                continue
            
            # Clean pricing
            try:
                price_cny = float(str(price_cny).replace(',', '').strip()) if price_cny is not None else 0.0
            except ValueError:
                price_cny = 0.0
                
            zh_name, ru_name = split_name(name_str)
            img_path = find_xlsx_image(f, sheetname, r_idx + 1)
            
            all_raw_products.append({
                "src": f,
                "sheet": sheetname,
                "row": r_idx + 1,
                "name_zh": zh_name,
                "name_ru": ru_name,
                "size": clean_size(size),
                "unit": str(unit).strip(),
                "price_cny": price_cny,
                "specs": clean_specs(specs),
                "image_path": img_path
            })

print(f"Collected {len(all_raw_products)} raw items from Excel files.")

# ==========================================
# PART 3: Parse PDF files
# ==========================================
print("\n--- Parsing PDF files ---")
pdf_jsons = [f for f in os.listdir(workspace) if f.endswith('_raw_pdf.json')]

for f in pdf_jsons:
    path = os.path.join(workspace, f)
    print(f"Processing PDF raw JSON: {f}")
    with open(path, 'r', encoding='utf-8') as jf:
        pages = json.load(jf)
    
    clean_fn = f.replace('_raw_pdf.json', '')
    pdf_img_dir = os.path.join(img_dir, f"pdf_{clean_fn}")
    
    # Collect all page images naturally sorted
    page_images = {}
    if os.path.exists(pdf_img_dir):
        for img_fn in os.listdir(pdf_img_dir):
            m = re.match(r"page_(\d+)_img_(\d+)_", img_fn)
            if m:
                p_num = int(m.group(1))
                img_idx = int(m.group(2))
                if p_num not in page_images:
                    page_images[p_num] = []
                page_images[p_num].append((img_idx, os.path.join(pdf_img_dir, img_fn)))
        
        # Sort each page's images by their original PDF image index
        for p_num in page_images:
            page_images[p_num] = [x[1] for x in sorted(page_images[p_num], key=lambda x: x[0])]

    # Parse items page-by-page
    for page in pages:
        p_num = page['page']
        text = page['text']
        
        lines = text.split('\n')
        page_items = []
        current_item = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Sequence detection
            m = re.match(r"^(\d+)(?:\s+([\u4e00-\u9fa5]+.*|[\w]+.*))?$", line)
            is_new = False
            num_val = -1
            name_part = ""
            if m:
                num_val = int(m.group(1))
                if num_val < 250:
                    name_part = m.group(2) if m.group(2) else ""
                    is_new = True
            
            if is_new:
                if current_item:
                    page_items.append(current_item)
                current_item = {
                    "id": num_val,
                    "lines": [name_part] if name_part else []
                }
            else:
                if current_item:
                    current_item["lines"].append(line)
        if current_item:
            page_items.append(current_item)
            
        # Clean and parse page items
        parsed_page_items = []
        for item in page_items:
            id_ = item["id"]
            ilines = item["lines"]
            text_content = " ".join(ilines)
            
            # Skip totals/headers
            if any(h in text_content for h in ['合计', 'Total', '单号', '收货', 'Buyer', 'Date', '微信', '支付宝', '购买须知', '此报价', '付款方式', '定金', '余款']):
                continue
            
            # Extract Qty, Price, Unit
            # Pattern: (PCS|台|套|个|支|SET|kg|m|M)?\s*(\d+)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)
            m_price = re.search(r"\b(PCS|台|套|个|支|SET|kg|m|M|PCS)\s+(\d+)\s+(\d+)\s+(\d+)\b", text_content, re.IGNORECASE)
            
            unit = "PCS"
            qty = 1
            price_cny = 0.0
            remains = text_content
            
            if m_price:
                unit = m_price.group(1)
                qty = int(m_price.group(2))
                price_cny = float(m_price.group(3))
                start, end = m_price.span()
                remains = text_content[:start] + " " + text_content[end:]
            else:
                # Gift pattern check: e.g. "2 0 0 赠送"
                m_gift = re.search(r"\b(PCS|台|套|个|支|SET|kg|m|M)?\s*(\d+)\s+0\s+0\s+(赠送客户|Gift\s+to\s+customers)", text_content, re.IGNORECASE)
                if m_gift:
                    unit = m_gift.group(1) if m_gift.group(1) else "PCS"
                    qty = int(m_gift.group(2))
                    price_cny = 0.0
                    start, end = m_gift.span()
                    remains = text_content[:start] + " " + text_content[end:]
            
            # Extract sizes
            sizes = re.findall(r"\b\d+(?:\.\d+)?\*\d+(?:\.\d+)?\*(?:\d+|\(\d+\+\d+\))\b|\b\d+(?:\.\d+)?\*\d+(?:\.\d+)?\*\d+(?:\+\d+)?\b|\b\d+格\b|\b\d+针\b", remains)
            size_str = ", ".join(sizes) if sizes else ""
            for s in sizes:
                remains = remains.replace(s, "")
            
            # Extract specs/power
            specs_list = re.findall(r"\b\d+V/\d+W\b|\b\d+V/\d+\.\d+KW\b|\b\d+V/\d+KW\b|\b\d+KW/\d+V\b|\b\d+V\b|\b\d+\.\d+KW\b|\b\d+KW\b|\b\d+V/\d+A\b", remains, re.IGNORECASE)
            spec_str = ", ".join(specs_list) if specs_list else ""
            for sp in specs_list:
                remains = remains.replace(sp, "")
                
            zh_name, ru_name = split_name(remains)
            
            parsed_page_items.append({
                "id": id_,
                "name_zh": zh_name,
                "name_ru": ru_name,
                "size": size_str,
                "unit": unit,
                "price_cny": price_cny,
                "specs": spec_str,
                "raw_text": text_content
            })
            
        # Map page items to page images sequentially
        # For Page 1, we often have a logo/header image first, so we might skip the first image
        # Let's check how many images we have on this page
        p_imgs = page_images.get(p_num, [])
        
        # Filter items that actually should have an image (skip free gifts or standard text-only accessories if M < N)
        # If there are images, we try to associate them
        if p_imgs:
            # Heuristic mapping:
            # If page 1, skip first image (logo) if total images > total items
            img_offset = 0
            if p_num == 1 and len(p_imgs) > len(parsed_page_items):
                img_offset = 1
            
            for item_idx, item in enumerate(parsed_page_items):
                img_idx = item_idx + img_offset
                if img_idx < len(p_imgs):
                    item["image_path"] = p_imgs[img_idx]
                else:
                    item["image_path"] = None
        else:
            for item in parsed_page_items:
                item["image_path"] = None
                
        # Append to all products
        for item in parsed_page_items:
            all_raw_products.append({
                "src": f,
                "sheet": f"page_{p_num}",
                "row": item["id"],
                "name_zh": item["name_zh"],
                "name_ru": item["name_ru"],
                "size": item["size"],
                "unit": item["unit"],
                "price_cny": item["price_cny"],
                "specs": item["specs"],
                "image_path": item["image_path"]
            })

print(f"Total raw products collected after parsing PDFs: {len(all_raw_products)}")

# ==========================================
# PART 4: Merging and Deduplication
# ==========================================
print("\n--- Merging and Deduplicating Products ---")

# Let's define a function to check if two products are identical
# We will match based on:
# 1. Cleaned Chinese name (if exists and is long enough)
# 2. Cleaned Russian name (if exists and is long enough)
# 3. Size and Price similarities

def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\u4e00-\u9fa5]", "", text) # keep alphanumeric and Chinese
    return text.strip()

merged_products = []

for raw in all_raw_products:
    zh_norm = normalize_text(raw["name_zh"])
    ru_norm = normalize_text(raw["name_ru"])
    
    # We ignore items with empty names
    if not zh_norm and not ru_norm:
        continue
        
    # Find duplicate in merged_products
    match_found = False
    for merged in merged_products:
        # Check matching criteria
        match_zh = (zh_norm and merged["zh_norm"] == zh_norm)
        match_ru = (ru_norm and merged["ru_norm"] == ru_norm)
        
        # If both names are very similar, or at least one is identical and sizes are close
        if (match_zh and match_ru) or (match_zh and not ru_norm) or (match_ru and not zh_norm) or (match_zh and normalize_text(raw["size"]) == normalize_text(merged["size"])):
            # Update values
            # If the raw product has an image, and the merged one doesn't (or the raw image is from an Excel file), update it
            if raw["image_path"] and (not merged["image_path"] or "xlsx_" in os.path.basename(raw["image_path"])):
                merged["image_path"] = raw["image_path"]
            
            # Combine specifications
            if raw["specs"] and raw["specs"] not in merged["specs"]:
                merged["specs"] = (merged["specs"] + ", " + raw["specs"]).strip(", ")
                
            # Keep the highest non-zero price (or most common price)
            if raw["price_cny"] > merged["price_cny"]:
                merged["price_cny"] = raw["price_cny"]
                
            # If name fields are missing or shorter in merged, update them
            if len(raw["name_zh"]) > len(merged["name_zh"]):
                merged["name_zh"] = raw["name_zh"]
            if len(raw["name_ru"]) > len(merged["name_ru"]):
                merged["name_ru"] = raw["name_ru"]
                
            match_found = True
            break
            
    if not match_found:
        merged_products.append({
            "name_zh": raw["name_zh"],
            "name_ru": raw["name_ru"],
            "zh_norm": zh_norm,
            "ru_norm": ru_norm,
            "size": raw["size"],
            "unit": raw["unit"],
            "price_cny": raw["price_cny"],
            "specs": raw["specs"],
            "image_path": raw["image_path"]
        })

print(f"Deduplicated from {len(all_raw_products)} to {len(merged_products)} unique products.")

# ==========================================
# PART 5: Copying and organizing images
# ==========================================
print("\n--- Organizing and Copying Images ---")

final_products = []
img_counter = 1

# Logical categorization function
def get_category(name_ru, name_zh):
    comb = (name_ru + " " + name_zh).lower()
    
    # Baskets / Tableware
    if any(x in comb for x in ['посуда', 'тарелка', 'блюдо', 'стакан', 'чашка', 'вилка', 'ложка', 'нож', 'салатник', 'соусник', 'чайник', 'кувшин', 'диспенсер для сока', 'бокал', 'ковш', 'кастрюля', 'сковорода', 'противень', 'гастроемкость', 'контейнер', 'корзина', 'ведро', 'поднос', 'солонка', 'перечница', 'щипцы', 'лопатка', 'венчик', 'шумовка', 'сито', 'доска разделочная', 'подставка для посуды', 'сетка', 'коврик', 'подсвечник', 'ваза', 'пепельница', 'салфетница', 'номерки', 'поднос']):
        return "tableware"
    # Coffee / Bar
    elif any(x in comb for x in ['кофе', 'coffee', 'кофемолка', 'миксер для молочных', 'блендер', 'соковыжималка', 'ледогенератор', '制冰机', 'ice maker', 'соковыжималка', 'сода', 'soda', 'сухогруз', 'сироп', 'барный', '开水器', 'кипятильник', 'водонагреватель', 'шейкер', 'питчер', 'риммер', 'джиггер', 'гейзер', 'мадлер', 'стрейнер', 'ложка барная', 'коврик барный', 'соковыжималка для цитрусовых']):
        return "bar"
    # Refrigeration
    elif any(x in comb for x in ['холодиль', 'морозиль', 'рефри', 'freezer', 'fridge', 'refriger', 'охлаждаем', '冷藏', '冷冻', '速冻', 'витрина холодильная', 'шкаф холодильный', 'стол холодильный', 'ларь морозильный', 'салат-бар', 'шоковая заморозка']):
        return "refrigeration"
    # Thermal
    elif any(x in comb for x in ['печь', 'oven', 'плита', 'stove', 'гриль', 'grill', 'фритюр', 'fryer', 'кипятильник', 'жарочный', 'пекарский', 'пароконвект', '蒸烤箱', 'котломойка', 'мармит', 'коптильня', 'вафельница', 'блинница', 'тостер', 'макароноварка', 'электроварка', 'слайсер для мяса', ' Salamander', 'панини', 'аппарат для шаурмы', 'попкорн', 'сахарная вата', 'рисоварка', 'термостат', 'sous-vide', 'су-вид']):
        return "thermal"
    # Electromechanical
    elif any(x in comb for x in ['миксер', 'mixer', 'мясорубка', 'grinder', 'тестомес', 'овощерезка', 'vegetable cutter', 'слайсер', 'slicer', 'куттер', 'хлеборезка', 'картофелечистка', 'тестораскатка', 'dough sheeter', 'фаршемешалка', 'пила для мяса', 'рыбочистка', 'шприц колбасный', 'прессы для гамбургеров', 'аппарат для пончиков', 'разрыхлитель мяса', 'тендерайзер']):
        return "electromechanical"
    # Neutral (Furniture & Steel)
    elif any(x in comb for x in ['стол', 'table', 'ванна моечная', 'раковина', 'sink', 'стеллаж', 'rack', 'полка', 'shelf', 'тележка', 'cart', 'подставка', 'стенд', 'шпилька', 'вешалка', 'шкаф нейтральный', 'нейтральное', 'вытяжной зонт', 'hood', 'подтоварник', 'рукосушитель', 'дозатор', 'урна', 'бак для мусора', 'скамья', 'вешалка для одежды', 'подставка под инвентарь']):
        return "neutral"
    # Furniture (Chairs, etc.)
    elif any(x in comb for x in ['стул', 'кресло', 'chair', 'диван', 'столешница', 'подстолье', 'вешалка', 'вешало', 'ширма', 'перегородка', 'зонт']):
        return "furniture"
    
    return "other"

for merged in merged_products:
    src_img = merged["image_path"]
    dest_img_name = "placeholder.jpg"
    
    if src_img and os.path.exists(src_img):
        # determine extension
        _, ext = os.path.splitext(src_img)
        if not ext:
            ext = ".jpg"
        if ext.lower() == '.jp2':
            ext = ".jpg" # converted
            
        dest_img_name = f"product_{img_counter}{ext.lower()}"
        dest_path = os.path.join(dest_img_dir, dest_img_name)
        
        try:
            # Copy
            shutil.copy2(src_img, dest_path)
            img_counter += 1
        except Exception as e:
            # print(f"  Error copying image {src_img}: {e}")
            dest_img_name = "placeholder.jpg"
    else:
        dest_img_name = "placeholder.jpg"
        
    category = get_category(merged["name_ru"], merged["name_zh"])
    
    # If price is 0, check if name contains "Gift" or "赠送"
    is_gift = (merged["price_cny"] == 0 or "gift" in (merged["name_ru"] + " " + merged["name_zh"]).lower() or "赠送" in merged["name_zh"])
    
    final_products.append({
        "id": len(final_products) + 1,
        "name_zh": merged["name_zh"],
        "name_ru": merged["name_ru"],
        "category": category,
        "size": merged["size"],
        "unit": merged["unit"],
        "price_cny": merged["price_cny"],
        "price_kzt": round(merged["price_cny"] * 73, 2),
        "specs": merged["specs"],
        "image": f"./images/{dest_img_name}",
        "is_gift": is_gift
    })

# Write products.json
out_json = os.path.join(workspace, "products.json")
with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(final_products, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully consolidated product database!")
print(f"Saved {len(final_products)} products to {out_json}")
print(f"Copied {img_counter-1} images to {dest_img_dir}")
