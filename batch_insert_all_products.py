#!/usr/bin/env python3
"""
Batch insert all 10 remaining products into const P array
Uses the insert_single_product.py logic
"""
import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

def escape_for_js(text):
    if not text:
        return ""
    text = text.replace('\\', '\\\\')
    text = text.replace('\r', '')
    text = text.replace('\n', '\\n')
    text = text.replace('\t', '\\t')
    text = text.replace('`', '\\`')
    text = text.replace('$', '\\$')
    return text

def find_const_p_bounds(content):
    """Return (start_of_array_bracket, end_of_closing_bracket) char positions"""
    start_marker = 'const P=['
    start_idx = content.find(start_marker)
    if start_idx < 0:
        return -1, -1

    i = start_idx + len(start_marker) - 1
    depth = 0
    in_str = False
    sc = ''
    escaped = False

    while i < len(content):
        c = content[i]
        if escaped:
            escaped = False
            i += 1
            continue
        if c == '\\':
            escaped = True
            i += 1
            continue
        if in_str:
            if c == sc:
                in_str = False
        else:
            if c in ('"', "'", '`'):
                in_str = True
                sc = c
            elif c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    return start_idx, i
        i += 1
    return -1, -1

def build_product_entry(product_id):
    base = Path("MD-ONLY-LIST")

    md_file = base / f"{product_id.lower()}-product-info.md"
    analysis_file = base / f"{product_id.upper()}-MD-ANALYSIS.md"
    meta_file = base / f"{product_id.upper()}-metadata.json"

    md_content = md_file.read_text(encoding='utf-8') if md_file.exists() else ""
    analysis_content = analysis_file.read_text(encoding='utf-8') if analysis_file.exists() else ""
    metadata = {}
    if meta_file.exists():
        try:
            metadata = json.loads(meta_file.read_text(encoding='utf-8'))
        except:
            pass

    # Determine product category defaults
    if "OLED" in product_id:
        dv, cat, sub, ico = "MS", "TV", "OLED evo", "📺"
        pr = metadata.get("price", "CAD $3,299.99")
        tags = '["OLED","AI","4K","MD-Only"]'
    elif product_id.startswith("LF"):
        dv, cat, sub, ico = "MS", "Appliance", "Refrigerator", "🧊"
        pr = metadata.get("price", "CAD $3,999.99")
        tags = '["LG","MD-Only"]'
    elif product_id.startswith("LK"):
        dv, cat, sub, ico = "MS", "Appliance", "Kimchi Refrigerator", "🌶"
        pr = metadata.get("price", "CAD $2,199.99")
        tags = '["LG","MD-Only"]'
    elif product_id.startswith(("WM", "WT")):
        dv, cat, sub, ico = "MS", "Appliance", "Washer", "👕"
        pr = metadata.get("price", "CAD $1,299.99")
        tags = '["LG","MD-Only"]'
    else:
        return None

    nm = metadata.get("name", product_id)
    url = metadata.get("url", f"https://www.lg.com/ca_en/")
    op = "Canada"

    md_esc = escape_for_js(md_content)
    an_esc = escape_for_js(analysis_content)

    entry = (
        f'{{id:"{product_id}",'
        f'dv:"{dv}",'
        f'cat:"{cat}",'
        f'sub:"{sub}",'
        f'ico:"{ico}",'
        f'nm:"{nm}",'
        f'pr:"{pr}",'
        f'op:"{op}",'
        f'url:"{url}",'
        f'crawled:false,'
        f'gal:[],'
        f'feat:[],'
        f'sp:{{}},'
        f'tags:{tags},'
        f'bul:[],'
        f'kw:"{nm}",'
        f'mdAnalysis:`{an_esc}`,'
        f'md:`{md_esc}`'
        f'}}'
    )
    return entry

def insert_product_batch(html_content, product_id):
    """Insert a product into the array"""
    # Find const P bounds
    array_start, array_end = find_const_p_bounds(html_content)
    if array_start < 0:
        return None, "[ERROR] Cannot find const P array"

    # Check if already in array
    array_content = html_content[array_start:array_end+2]
    if f'id:"{product_id}"' in array_content:
        return html_content, f"[SKIP] Already in array"

    # Build entry
    entry = build_product_entry(product_id)
    if not entry:
        return None, "[ERROR] Cannot build product entry"

    # Insert before closing ]
    insert_pos = array_end
    updated_content = (
        html_content[:insert_pos] +
        f',{entry}' +
        html_content[insert_pos:]
    )

    return updated_content, "[OK] Inserted"

# Main
print("=" * 70)
print("BATCH INSERT: All 10 Remaining Products")
print("=" * 70)

html_file = Path("LG_AI_Content_Hub_v6_20.html")
html_content = html_file.read_text(encoding='utf-8')

print(f"\nStarting file size: {len(html_content):,} chars")

products = [
    'OLED55C5PUA',
    'OLED83C5PUA',
    'LF25S6560S',
    'LF30S8210S',
    'LF29S8365S',
    'LF25Z6211S',
    'LK14S8000V',
    'WM6700HBA',
    'WM8900HBA',
    'WT8600CB',
]

success_count = 0
skip_count = 0

for product_id in products:
    result, msg = insert_product_batch(html_content, product_id)
    print(f"\n[INSERT] {product_id}")
    print(f"  {msg}")

    if result is None:
        print(f"  [FATAL] Failed!")
        exit(1)
    elif result == html_content:
        skip_count += 1
    else:
        html_content = result
        success_count += 1

# Verify file is still valid
if 'function renderList' not in html_content:
    print("\n[ERROR] renderList function missing!")
    exit(1)

if 'const P=[' not in html_content:
    print("\n[ERROR] const P array missing!")
    exit(1)

# Write back
html_file.write_text(html_content, encoding='utf-8')

print()
print("=" * 70)
print(f"BATCH INSERT COMPLETE")
print("=" * 70)
print(f"Inserted: {success_count}")
print(f"Skipped: {skip_count}")
print(f"Final file size: {len(html_content):,} chars")

