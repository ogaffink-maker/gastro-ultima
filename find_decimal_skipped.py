import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
workspace = r"c:\Users\Auditore\Downloads\price list"

pdf_files = [f for f in os.listdir(workspace) if f.endswith('_raw_pdf.json')]

for pf in pdf_files:
    pf_path = os.path.join(workspace, pf)
    with open(pf_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Checking {pf}...")
    for page in data:
        text = page['text']
        # Search for lines containing decimal numbers near PCS/台/套/个/支/SET
        lines = text.split('\n')
        for line in lines:
            if re.search(r'\b(PCS|台|套|个|支|SET)\b', line, re.IGNORECASE) and re.search(r'\b\d+\.\d+\b', line):
                print(f"  Page {page['page']}: {line.strip()}")
