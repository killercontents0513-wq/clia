#!/usr/bin/env python3
"""
Insert a single product into const P array correctly.
Also removes any duplicate/orphaned occurrences outside the array.
"""
import json
import re
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

    # start scanning from the '[' character
    i = start_idx + len(start_marker) - 1  # position of '['
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
                    # Found the closing ']', confirm ';' follows
                    if i + 1 < len(content) and content[i + 1] == ';':
                        return start_idx, i  # i = position of ']'
                    else:
                        return start_idx, i
        i += 1
    return -1, -1

def remove_orphaned_products(content, product_id, array_start, array_end):
    """Remove product definitions that exist OUTSIDE the const P array"""
    pattern = re.compile(
        r',?\s*\{id:"' + re.escape(product_id) + r'".*?(?:md:`(?:[^`]|\\`)*`)\}',
        re.DOTALL
    )

    removed = 0
    # Find all matches and remove those outside array bounds
    for match in reversed(list(pattern.finditer(content))):
        s, e = match.start(), match.end()
        if s > array_end or e < array_start:
            # Outside array — remove
            content = content[:s] + content[e:]
            removed += 1
            print(f"  Removed orphaned {product_id} at position {s}")

    return content, removed

def build_product_entry(product_id):
    base = Path("C:/Users/Administrator/Desktop/AI/RetailOBS/3P/MD-ONLY-LIST")

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
    url = metadata.get("url", f"https://www.lg.com/ca_en/tv-soundbars/oled-evo/{product_id.lower()}/")
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

def insert_product(product_id):
    html_file = Path("C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html")
    content = html_file.read_text(encoding='utf-8')

    print(f"\n[INSERT] {product_id}")
    print(f"File size: {len(content):,} chars")

    # Find const P bounds
    array_start, array_end = find_const_p_bounds(content)
    if array_start < 0:
        print("[ERROR] Cannot find const P array")
        return False
    print(f"const P: chars {array_start:,} to {array_end:,}")

    # Check if already in array
    array_content = content[array_start:array_end+2]
    if f'id:"{product_id}"' in array_content:
        print(f"[SKIP] {product_id} already in const P array")
        return True

    # Remove any orphaned duplicates outside the array
    content, removed = remove_orphaned_products(content, product_id, array_start, array_end)
    if removed:
        # Recalculate bounds after removal
        array_start, array_end = find_const_p_bounds(content)
        print(f"After cleanup, const P: chars {array_start:,} to {array_end:,}")

    # Build entry
    entry = build_product_entry(product_id)
    if not entry:
        print(f"[ERROR] Cannot build entry for {product_id}")
        return False

    md_size = len(entry)
    print(f"Entry size: {md_size:,} chars")

    # Insert BEFORE the closing ']' of const P
    # array_end points to the ']' character
    insert_pos = array_end  # insert before ']'

    before = content[:insert_pos]
    after = content[insert_pos:]

    new_content = before + ',' + entry + after

    # Verify
    new_start, new_end = find_const_p_bounds(new_content)
    new_array = new_content[new_start:new_end+2]
    count = new_array.count('id:"')
    in_array = f'id:"{product_id}"' in new_array

    print(f"Verification: {product_id} in array: {in_array}, total products: {count}")

    if in_array:
        html_file.write_text(new_content, encoding='utf-8')
        print(f"[SUCCESS] {product_id} inserted. Products in const P: {count}")
        return True
    else:
        print(f"[FAILED] Verification failed — file NOT written")
        return False

if __name__ == '__main__':
    import sys
    product_id = sys.argv[1] if len(sys.argv) > 1 else "OLED77C5PUA"
    success = insert_product(product_id)
    exit(0 if success else 1)
