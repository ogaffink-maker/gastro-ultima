import sys
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

reader = PdfReader("930010单哈萨克斯坦客户报价清单9.30日.pdf")
for i, page in enumerate(reader.pages):
    print(f"Page {i+1}: Rotate={page.get('/Rotate')}, MediaBox={page.mediabox}")
