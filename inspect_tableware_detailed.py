import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

# Keywords to find all kitchen utensils/tableware
keywords = [
    'посуда', 'тарелка', 'блюдо', 'стакан', 'чашка', 'вилка', 'ложка', 'нож', 'салатник', 
    'соусник', 'чайник', 'кувшин', 'диспенсер', 'бокал', 'ковш', 'кастрюля', 'сковорода', 
    'противень', 'гастроемкость', 'контейнер', 'корзина', 'ведро', 'поднос', 'солонка', 
    'перечница', 'щипцы', 'лопатка', 'венчик', 'шумовка', 'сито', 'доска разделочная', 
    'подставка для посуды', 'сетка', 'коврик', 'подсвечник', 'ваза', 'пепельница', 
    'салфетница', 'номерки', 'мусат', 'точильный', 'прихватка', 'термометр', 'весы',
    'скребок', 'кисточка', 'пинцет', 'дуршлаг', 'чеснокодавка', 'сотейник',
    'tongs', 'ladle', 'skimmer', 'spatula', 'spoon', 'whisk', 'masher', 'grater', 'peeler',
    'scraper', 'brush', 'bowl', 'colander', 'strainer', 'container', 'board', 'dispenser',
    'sharpener', 'scissors', 'opener', 'corkscrew', 'pitcher', 'kettle', 'pot', 'pan',
    'sauce', 'thermometer', 'timer', 'scale', 'basket', 'ruler'
]

tableware_items = []
for p in products:
    name_ru = p.get('name_ru', '').lower()
    name_zh = p.get('name_zh', '').lower()
    if any(k in name_ru or k in name_zh for k in keywords):
        tableware_items.append(p)

print(f"Total tableware items found: {len(tableware_items)}")
for p in tableware_items[:150]:
    print(f"ID: {p['id']:<4} | Price: {p['price_cny']:<6} | Image: {p['image']:<25} | RU: {p['name_ru'][:40]:<40} | ZH: {p['name_zh'][:20]}")
