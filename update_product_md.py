#!/usr/bin/env python3
"""
Update existing products in const P array with new md field content.
This script finds existing products and updates their md field with standardized markdown.
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

    # Find the start of this object (search backward for '{')
    obj_start = array_content.rfind('{', 0, idx)
    if obj_start < 0:
        return -1, -1

    # Find the end of this object (search forward for '}')
    # Need to handle nested braces and strings
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

def update_product(product_id):
    html_file = Path("LG_AI_Content_Hub_v6_20.html")
    content = html_file.read_text(encoding='utf-8')

    print(f"\n[UPDATE] {product_id}")
    print(f"File size: {len(content):,} chars")

    # Find const P bounds
    array_start, array_end = find_const_p_bounds(content)
    if array_start < 0:
        print("[ERROR] Cannot find const P array")
        return False

    print(f"const P: chars {array_start:,} to {array_end:,}")

    # Extract array content
    array_content = content[array_start:array_end+1]

    # Find product in array
    prod_start, prod_end = find_product_in_array(array_content, product_id)
    if prod_start < 0:
        print(f"[ERROR] {product_id} not found in array")
        return False

    print(f"Product found at relative positions {prod_start:,} to {prod_end:,}")

    # Read markdown content
    md_file = Path(f"MD-ONLY-LIST/{product_id.lower()}-product-info.md")
    if not md_file.exists():
        print(f"[ERROR] Markdown file not found: {md_file}")
        return False

    md_content = md_file.read_text(encoding='utf-8')
    md_esc = escape_for_js(md_content)

    print(f"Markdown file: {len(md_content):,} chars → {len(md_esc):,} chars (escaped)")

    # Extract the product object
    product_obj = array_content[prod_start:prod_end]

    # Check if md field already exists
    if 'md:`' in product_obj:
        # Replace existing md field
        print("Replacing existing md field...")
        # Find the md field and replace it
        md_pattern = r'md:`[^`]*(?:\\`[^`]*)*`'
        new_md = f'md:`{md_esc}`'
        updated_obj = re.sub(md_pattern, new_md, product_obj, count=1)
    else:
        # Add md field before closing }
        print("Adding new md field...")
        updated_obj = product_obj[:-1] + f',md:`{md_esc}`' + '}'

    # Verify the update
    if updated_obj == product_obj:
        print("[WARNING] Product object unchanged!")
        return False

    # Replace in array content
    updated_array = array_content[:prod_start] + updated_obj + array_content[prod_end:]

    # Replace in full content
    updated_content = content[:array_start] + updated_array + content[array_end+1:]

    # Write back
    html_file.write_text(updated_content, encoding='utf-8')

    print(f"[SUCCESS] {product_id} updated")
    print(f"New file size: {len(updated_content):,} chars")

    return True

if __name__ == '__main__':
    # Update both products
    for product_id in ['OLED65C5PUA', 'OLED77C5PUA']:
        if not update_product(product_id):
            print(f"Failed to update {product_id}")
            break
