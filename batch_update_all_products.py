#!/usr/bin/env python3
"""
Batch update all 10 remaining products into const P array with md field
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

def find_product_in_array(array_content, product_id):
    """Find start and end positions of product object in array content"""
    pattern = f'id:"{product_id}"'
    idx = array_content.find(pattern)
    if idx < 0:
        return -1, -1

    obj_start = array_content.rfind('{', 0, idx)
    if obj_start < 0:
        return -1, -1

    i = idx
    depth = 0
    in_str = False
    sc = ''
    escaped = False

    while i < len(array_content):
        c = array_content[i]
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
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return obj_start, i + 1
        i += 1

    return -1, -1

def update_product(html_content, product_id):
    """Update a single product and return updated html_content"""
    print(f"\n[UPDATE] {product_id}")

    # Find const P bounds
    array_start, array_end = find_const_p_bounds(html_content)
    if array_start < 0:
        print(f"  [ERROR] Cannot find const P array")
        return None

    # Extract array content
    array_content = html_content[array_start:array_end+1]

    # Find product in array
    prod_start, prod_end = find_product_in_array(array_content, product_id)
    if prod_start < 0:
        print(f"  [SKIP] {product_id} not found in array")
        return html_content

    # Read markdown content
    md_file = Path(f"MD-ONLY-LIST/{product_id.lower()}-product-info.md")
    if not md_file.exists():
        print(f"  [ERROR] Markdown file not found")
        return None

    md_content = md_file.read_text(encoding='utf-8')
    md_esc = escape_for_js(md_content)

    # Extract the product object
    product_obj = array_content[prod_start:prod_end]

    # Check if md field already exists
    if 'md:`' in product_obj:
        # Replace existing md field
        md_pattern = r'md:`[^`]*(?:\\`[^`]*)*`'
        new_md = f'md:`{md_esc}`'
        updated_obj = re.sub(md_pattern, new_md, product_obj, count=1)
    else:
        # Add md field before closing }
        updated_obj = product_obj[:-1] + f',md:`{md_esc}`' + '}'

    # Replace in array content
    updated_array = array_content[:prod_start] + updated_obj + array_content[prod_end:]

    # Replace in full content
    updated_content = html_content[:array_start] + updated_array + html_content[array_end+1:]

    print(f"  [OK] Updated with {len(md_esc):,} chars (escaped)")
    return updated_content

# Main
print("=" * 70)
print("BATCH UPDATE: All 10 Remaining Products")
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
    result = update_product(html_content, product_id)
    if result is None:
        print(f"  [FATAL] Failed to update {product_id}")
        exit(1)
    elif result == html_content:
        skip_count += 1
    else:
        html_content = result
        success_count += 1

# Verify file is still valid
if 'function renderList' not in html_content:
    print("\n[ERROR] renderList function missing - file may be corrupted!")
    exit(1)

if 'const P=[' not in html_content:
    print("\n[ERROR] const P array missing - file may be corrupted!")
    exit(1)

# Write back
html_file.write_text(html_content, encoding='utf-8')

print()
print("=" * 70)
print(f"BATCH UPDATE COMPLETE")
print("=" * 70)
print(f"Updated: {success_count}")
print(f"Skipped: {skip_count}")
print(f"Final file size: {len(html_content):,} chars")
print()
print("✓ All products integrated successfully!")

