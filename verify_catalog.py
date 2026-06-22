import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

workspace = r"c:\Users\Auditore\Downloads\price list"
json_path = os.path.join(workspace, "products.json")
images_dir = os.path.join(workspace, "images")

print("Starting validation checks on products.json...")

if not os.path.exists(json_path):
    print("FAIL: products.json does not exist!")
    sys.exit(1)

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
except Exception as e:
    print(f"FAIL: Failed to parse products.json as JSON: {e}")
    sys.exit(1)

print(f"Loaded {len(products)} products from products.json.")

valid_categories = {'thermal', 'refrigeration', 'electromechanical', 'bar', 'neutral', 'tableware', 'furniture', 'other'}
errors = []
warnings = []
ids = set()

for idx, p in enumerate(products):
    p_id = p.get('id')
    name_ru = p.get('name_ru')
    name_zh = p.get('name_zh')
    price_cny = p.get('price_cny')
    price_kzt = p.get('price_kzt')
    category = p.get('category')
    image = p.get('image')
    
    # 1. Unique ID
    if p_id is None:
        errors.append(f"Product {idx}: ID is missing.")
    elif p_id in ids:
        errors.append(f"Product {idx}: Duplicate ID {p_id}.")
    else:
        ids.add(p_id)
        
    # 2. Name check
    if not name_ru and not name_zh:
        errors.append(f"Product {idx} (ID {p_id}): Both name_ru and name_zh are empty.")
        
    # 3. Currency rate check (price_kzt == price_cny * 73)
    if price_cny is None or price_kzt is None:
        errors.append(f"Product {idx} (ID {p_id}): Price is missing.")
    else:
        expected_kzt = round(price_cny * 73, 2)
        if abs(price_kzt - expected_kzt) > 0.01:
            errors.append(f"Product {idx} (ID {p_id}): Exchange rate mismatch. Price CNY: {price_cny}, Price KZT: {price_kzt}, Expected KZT: {expected_kzt}")
            
    # 4. Category check
    if not category:
        errors.append(f"Product {idx} (ID {p_id}): Category is missing.")
    elif category not in valid_categories:
        errors.append(f"Product {idx} (ID {p_id}): Invalid category '{category}'.")
        
    # 5. Image existence check
    if not image:
        errors.append(f"Product {idx} (ID {p_id}): Image path is missing.")
    else:
        # Resolve image path relative to workspace
        # image value is e.g. "./images/product_1.jpg"
        clean_img_path = image.replace('./', '').replace('/', '\\')
        full_img_path = os.path.join(workspace, clean_img_path)
        if "placeholder.jpg" in image:
            # this is a fallback placeholder, acceptable warning
            warnings.append(f"Product {p_id} ('{name_ru[:30]}...'): Uses placeholder image.")
        elif not os.path.exists(full_img_path):
            errors.append(f"Product {p_id} ('{name_ru[:30]}...'): Referenced image {image} does not exist at {full_img_path}!")

print(f"\n--- Validation Summary ---")
print(f"Total Products Checked: {len(products)}")
print(f"Total Errors Found: {len(errors)}")
print(f"Total Warnings Found: {len(warnings)}")

if warnings:
    print(f"\nWarnings (first 10 shown):")
    for w in warnings[:10]:
        print(f"  [WARN] {w}")
    if len(warnings) > 10:
        print(f"  ... and {len(warnings) - 10} more warnings")

if errors:
    print(f"\nErrors (first 20 shown):")
    for e in errors[:20]:
        print(f"  [ERROR] {e}")
    if len(errors) > 20:
        print(f"  ... and {len(errors) - 20} more errors")
    print("\nFAIL: Products catalog has errors!")
    sys.exit(1)
else:
    print("\nSUCCESS: All validation checks passed successfully!")
