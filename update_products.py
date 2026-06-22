import json
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
workspace = r"c:\Users\Auditore\Downloads\price list"
json_path = os.path.join(workspace, "products.json")

# 1. Load products
with open(json_path, 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"Initial products count: {len(products)}")

# 2. QR Candidates from check
qr_images = {
    'product_82.jpg',
    'product_193.jpg',
    'product_194.jpg',
    'product_228.jpg',
    'product_243.jpg',
    'product_318.jpg',
    'product_338.jpg',
    'product_339.jpg'
}

# 3. Translation and normalization dictionary
translations = {
    "四门冷藏柜": "Четырехдверный холодильный шкаф (1210x760x1980 мм)",
    "4\"方柱双层盘": "Квадратная двухъярусная тарелка 4\"",
    "8\"皇冠点心碗": "Десертная чаша-корона 8\"",
    "13\"石纹鹅卵石盘": "Блюдо с текстурой камня 'Галька' 13\"",
    "11.5\"矮身浪纹保温盘": "Глубокая тарелка с волнистой текстурой 11.5\"",
    "10\"树形罗纹盘": "Блюдо с древесной текстурой 10\"",
    "10\"内石纹外荷口保温盘": "Глубокое блюдо с текстурой камня 10\"",
    "8\"圆形珠点双层盘": "Круглое двухъярусное блюдо с жемчужным узором 8\"",
    "8.5\"珊瑚盘": "Блюдо с коралловым узором 8.5\"",
    "9.5寸八爪鱼盘": "Круглая тарелка с рисунком осьминога 9.5\"",
    "10\"圆形保温盘": "Круглое плоское блюдо 10\"",
    "10\"方形双层盘": "Квадратное двухъярусное блюдо 10\"",
    "9\"漩涡保温盘": "Блюдо с текстурой вихря 9\"",
    "10\"圆桌": "Глубокая круглая тарелка 10\"",
    "6.5寸岩石纹碗": "Салатник с текстурой скалы 6.5\"",
    "8.5寸岩石纹碗": "Салатник с текстурой скалы 8.5\"",
    "普通木架": "Деревянная обрешетка (упаковочная рама)",
    "全自动意大利机": "Автоматическая эспрессо кофемашина",
    "12寸切片机": "Слайсер профессиональный 12 дюймов (300 мм)",
    "45手提搅拌器": "Ручной погружной блендер 45",
    "304吧匙 304 bar spoon 9寸": "Барная ложка 304 (9 дюймов / 23 см)",
    "304吧匙 304 bar spoon 12寸": "Барная ложка 304 (12 дюймов / 30 см)",
    "风冷单大门冷冻厨房柜Однодверный кухонный шкаф с морозильной камерой с воздушным охлаждением": "Однодверный кухонный морозильный шкаф с воздушным охлаждением",
    "Стол-морозильник 冷冻柜     Freezer table": "Стол-морозильник кухонный",
    "Шкаф морозильный 冷冻柜    Upright freezer cabinet": "Шкаф морозильный вертикальный",
    "Льдогенератор 120kg制冰机 735*603*1010660x6 80x900   Ice maker": "Льдогенератор кубикового льда 120 кг/сутки",
    "Морозильник 冰箱冷冻室    Upright freezer": "Морозильный шкаф вертикальный",
    "双大门冷藏柜 Double door refrigerated cabinet    1~8°C": "Двухдверный холодильный шкаф (1~8°C)",
    "双大门冷冻柜 Double door freezer    ·-18°~-22°": "Двухдверный морозильный шкаф (-18°~-22°)",
    "冷藏柜 Refrigeration workstation": "Холодильный стол с воздушным охлаждением",
    "智能触摸板十盘万能蒸烤 箱 自动清洗 Intelligent touchpad ten disc universal steaming oven Automatic cleaning": "Пароконвектомат инжекторный на 10 уровней с автоматической мойкой",
    "万能蒸烤箱底架 Universal steaming oven frame": "Подставка под пароконвектомат",
    "分体式制冰机方冰 Split type ice maker square ice    制冰量 250KG/天 Ice making capacity 250KG/day": "Льдогенератор кубикового льда 250 кг/сутки",
    "欧款双大门冷藏柜 European style double door refrigerated cabinet 1.4M": "Двухдверный холодильный шкаф 1.4 м",
    "风冷冷冻工作台 Air cooled refrigeration workbench": "Морозильный стол с воздушным охлаждением",
    "牛奶冷藏冰箱 Milk refrigerated refrigerator   温度保持在1-5摄氏度，容量为8-10 升。": "Холодильник для молока (8-10 л, 1-5°C)",
    "豪华款风冷冷冻柜 Luxury air-cooled freezer": "Морозильный шкаф премиум с воздушным охлаждением",
    "豪华款风冷冷藏柜 Luxury Wind Cold Storage Cabinet": "Холодильный шкаф премиум с воздушным охлаждением",
    "风冷冷藏操作台 Air-cooled refrigeration workbench +170": "Холодильный стол с воздушным охлаждением"
}

# Regex cleanups for common Chinese characters remaining in Russian text
def clean_russian_field(text):
    if not text:
        return ""
    # Remove Chinese characters
    text = re.sub(r"[\u4e00-\u9fa5]", "", text)
    # Clean up multiple whitespaces
    text = re.sub(r"\s+", " ", text)
    # Remove trailing/leading symbols like slashes or dots
    text = text.strip(" .;,-/")
    return text

updated_products = []
id_counter = 1

for p in products:
    name_ru = p.get('name_ru', '').strip()
    name_zh = p.get('name_zh', '').strip()
    price_cny = p.get('price_cny', 0)
    is_gift = p.get('is_gift', False)
    
    # 1. Skip gifts
    if is_gift or price_cny == 0 or "подарок" in name_ru.lower() or "赠送" in name_zh:
        # print(f"Skipping Gift: {name_ru or name_zh}")
        continue
    
    # 2. Check direct dictionary matches
    # Match Chinese name or exact Chinese+Russian combo
    matched = False
    
    # Search dictionary keys in Chinese name or Russian name
    for k, v in translations.items():
        if k in name_zh or k in name_ru:
            name_ru = v
            matched = True
            break
            
    # If Russian name is empty or "Без названия", translate it
    if not matched and (not name_ru or name_ru.lower() in ['без названия', 'no name', '']):
        # Apply generic translations based on keywords
        if "盘" in name_zh or "碟" in name_zh:
            name_ru = f"Блюдо / Тарелка {name_zh}"
        elif "碗" in name_zh:
            name_ru = f"Салатник / Чаша {name_zh}"
        elif "柜" in name_zh:
            name_ru = f"Холодильный / Морозильный шкаф {name_zh}"
        elif "木架" in name_zh:
            name_ru = "Деревянный каркас (обрешетка)"
        elif "机" in name_zh:
            name_ru = f"Профессиональное оборудование {name_zh}"
        else:
            name_ru = name_zh
            
    # Clean up Russian field from any remaining Chinese text
    name_ru = clean_russian_field(name_ru)
    
    # Check if Russian name is empty after cleanups
    if not name_ru:
        name_ru = "Профессиональное оборудование"
        
    # Replace QR code images
    image = p.get('image', '')
    if image:
        img_fn = os.path.basename(image)
        if img_fn in qr_images:
            print(f"Replacing QR code image {img_fn} for ID {p['id']} with placeholder")
            image = "./images/placeholder.jpg"
            
    p['id'] = id_counter
    p['name_ru'] = name_ru
    p['name_zh'] = name_zh
    p['image'] = image
    p['price_kzt'] = round(price_cny * 73, 2)
    
    updated_products.append(p)
    id_counter += 1

# Write back updated products.json
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(updated_products, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully updated products database!")
print(f"New count: {len(updated_products)} (from {len(products)})")
print(f"Saved to {json_path}")
