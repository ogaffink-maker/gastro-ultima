import json
import os
import sys
import re
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')
workspace = r"c:\Users\Auditore\Downloads\price list"
pdf_path = os.path.join(workspace, "930010单哈萨克斯坦客户报价清单9.30日.pdf")

reader = PdfReader(pdf_path)

def inspect_page_layout(page_idx):
    page = reader.pages[page_idx]
    contents = page.get('/Contents')
    if not contents:
        return []
    if isinstance(contents, list):
        data = b"".join(c.get_data() for c in contents)
    elif hasattr(contents, 'get_data'):
        data = contents.get_data()
    else:
        data = b""
    text_data = data.decode('latin-1')
    
    # Match matrix numbers and Do operator
    pattern = r"([-\d\.\s]+)cm\s*(?:q\s*)?/(\w+)\s+Do"
    matches = re.findall(pattern, text_data)
    
    placements = []
    for matrix, name in matches:
        parts = [float(x) for x in matrix.strip().split()]
        if len(parts) == 6:
            w, _, _, h, x, y = parts
            placements.append({
                "name": name,
                "x": x,
                "y": y,
                "w": w,
                "h": h
            })
            
    print(f"--- Page {page_idx + 1} Image Placements (Raw Order in Stream) ---")
    for idx, pl in enumerate(placements):
         print(f"Index {idx}: Name={pl['name']}, X={pl['x']:.2f}, Y={pl['y']:.2f}, W={pl['w']:.2f}, H={pl['h']:.2f}")
         
    # Let's sort by Y descending
    y_sorted = sorted(placements, key=lambda p: p["y"], reverse=True)
    print("\n--- Sorted by Y descending ---")
    for idx, pl in enumerate(y_sorted):
         print(f"Index {idx}: Name={pl['name']}, X={pl['x']:.2f}, Y={pl['y']:.2f}")

    # Let's try grouping into rows (within e.g. 20 points of Y)
    rows = []
    for pl in placements:
        added = False
        for row in rows:
            # Check if Y is close to the average Y of the row
            avg_y = sum(item["y"] for item in row) / len(row)
            if abs(pl["y"] - avg_y) < 30:
                row.append(pl)
                added = True
                break
        if not added:
            rows.append([pl])
            
    # Sort rows by their average Y descending
    rows = sorted(rows, key=lambda r: sum(item["y"] for item in r)/len(r), reverse=True)
    
    # Sort items within each row by X ascending
    grid_sorted = []
    print("\n--- Sorted by Grid (Rows of Y descending, then X ascending) ---")
    for r_idx, row in enumerate(rows):
        row_sorted = sorted(row, key=lambda item: item["x"])
        print(f"Row {r_idx + 1}:")
        for pl in row_sorted:
            print(f"  Name={pl['name']}, X={pl['x']:.2f}, Y={pl['y']:.2f}")
            grid_sorted.append(pl)
            
    return placements

print("Page 7 (0-indexed page index 6):")
inspect_page_layout(6)

print("\n\nPage 8 (0-indexed page index 7):")
inspect_page_layout(7)
