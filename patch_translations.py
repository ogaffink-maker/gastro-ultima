import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
workspace = r"c:\Users\Auditore\Downloads\price list"
json_path = os.path.join(workspace, "products.json")

with open(json_path, 'r', encoding='utf-8') as f:
    products = json.load(f)

# A detailed patch dictionary for translating Chinese terms to proper professional Russian terms
patches = {
    "全自动意大利机": "Аппарат для приготовления пасты (макаронопресс)",
    "六头方型煲仔炉": "Плита индукционная 6-конфорочная (煲仔)",
    "10盘万能蒸烤箱": "Пароконвектомат инжекторный на 10 уровней",
    "万能蒸烤箱底架": "Подставка под пароконвектомат",
    "升降面火炉": "Гриль-Саламандра электрический (Salamander)",
    "风冷六抽冷藏工作台": "Холодильный стол с 6 выдвижными ящиками",
    "风冷双大门冷藏厨房柜": "Холодильный шкаф кухонный двухдверный",
    "风冷双大门冷冻厨房柜": "Морозильный шкаф кухонный двухдверный",
    "低温慢煮机": "Аппарат низкотемпературной варки (Су-Вид / Sous-Vide)",
    "新款250 10寸半自动切片机": "Слайсер полуавтоматический 10 дюймов (250 мм)",
    "风冷九抽冷藏工作台": "Холодильный стол с 9 выдвижными ящиками",
    "台式电磁炉": "Настольная индукционная плита",
    "60系列304餐炉": "Мармит (Chafing Dish) настольный серия 60",
    "20L搅拌机": "Планетарный миксер 20 литров",
    "长方形烟罩": "Зонт вентиляционный вытяжной прямоугольный",
    "风冷单大门冷冻厨房柜": "Морозильный шкаф кухонный однодверный",
    "Шортенер": "Жироуловитель / Сборник шортенер",
    "Hamilton Beach": "Блендер профессиональный Hamilton Beach",
    "大理石面粉操作台": "Стол для работы с тестом с мраморной столешницей",
    "四门冷藏柜": "Холодильный шкаф четырехдверный",
    "12寸切片机": "Слайсер полуавтоматический 12 дюймов (300 мм)",
    "45手提搅拌器": "Погружной блендер ручной 45",
    "智能触摸板十盘万能蒸烤 箱 自动清洗": "Пароконвектомат инжекторный на 10 уровней с автоматической мойкой",
    "分体式制冰机方冰": "Льдогенератор кубикового льда (с бункером) 250 кг/сутки",
    "欧款双大门冷藏柜": "Холодильный шкаф кухонный двухдверный 1.4 м",
    "风冷冷冻工作台": "Морозильный стол кухонный с воздушным охлаждением",
    "牛奶冷藏冰箱": "Холодильник для молока (8-10 л, 1-5°C)",
    "豪华款风冷冷冻柜": "Морозильный шкаф премиум с воздушным охлаждением",
    "豪华款风冷冷藏柜": "Холодильный шкаф премиум с воздушным охлаждением",
    "风冷冷藏操作台": "Холодильный стол кухонный с воздушным охлаждением"
}

patched_count = 0
for p in products:
    name_zh = p.get('name_zh', '')
    name_ru = p.get('name_ru', '')
    
    # Apply patches based on Chinese terms
    matched = False
    for k, v in patches.items():
        if k in name_zh or k in name_ru:
            p['name_ru'] = v
            matched = True
            patched_count += 1
            break
            
    # Additional cleanups
    if 'глиняная печь' in p['name_ru'].lower():
        p['name_ru'] = "Печь для глиняных горшков 6-конфорочная"
        patched_count += 1
    if 'итальян' in p['name_ru'].lower() and 'кофе' in p['name_ru'].lower():
        p['name_ru'] = "Аппарат для приготовления пасты (макаронопресс)"
        patched_count += 1
    if 'сиши' in p['name_ru'].lower() or 'сиши' in p['name_zh']:
        p['name_ru'] = "Рисоварка профессиональная (西施煲)"
        patched_count += 1

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"Patched {patched_count} products with professional translations!")
