#!/usr/bin/env python3
"""
CLEAN FIX: Remove incorrectly placed products and properly integrate 11 priority products into const P array
"""
import json
import re
from pathlib import Path

def escape_for_javascript(text):
    """Escape text for JavaScript template literal"""
    if not text:
        return ""
    text = text.replace('\\', '\\\\')
    text = text.replace('\r', '\\r')
    text = text.replace('\n', '\\n')
    text = text.replace('\t', '\\t')
    text = text.replace('`', '\\`')
    text = text.replace('$', '\\$')
    return text

def read_markdown_file(product_id):
    md_file = Path(f"C:/Users/Administrator/Desktop/AI/RetailOBS/3P/MD-ONLY-LIST/{product_id.lower()}-product-info.md")
    if md_file.exists():
        return md_file.read_text(encoding='utf-8')
    return ""

def read_analysis_file(product_id):
    analysis_file = Path(f"C:/Users/Administrator/Desktop/AI/RetailOBS/3P/MD-ONLY-LIST/{product_id.upper()}-MD-ANALYSIS.md")
    if analysis_file.exists():
        return analysis_file.read_text(encoding='utf-8')
    return ""

def read_metadata(product_id):
    meta_file = Path(f"C:/Users/Administrator/Desktop/AI/RetailOBS/3P/MD-ONLY-LIST/{product_id.upper()}-metadata.json")
    if meta_file.exists():
        try:
            return json.loads(meta_file.read_text(encoding='utf-8'))
        except:
            pass
    return {}

def create_product_code(product_id):
    """Create JavaScript product object code"""
    md_content = read_markdown_file(product_id)
    analysis_content = read_analysis_file(product_id)
    metadata = read_metadata(product_id)

    # Determine category
    if "OLED" in product_id:
        dv = "MS"
        cat = "TV"
        sub = "OLED evo"
        ico = "📺"
        pr = "CAD $1,699.99"
        tags = '["OLED","AI","4K","MD-Only"]'
    elif product_id.startswith("LF"):
        dv = "MS"
        cat = "Appliance"
        sub = "Refrigerator"
        ico = "🧊"
        pr = "CAD $3,999.99"
        tags = '["LG","MD-Only"]'
    elif product_id.startswith("LK"):
        dv = "MS"
        cat = "Appliance"
        sub = "Kimchi Refrigerator"
        ico = "🌶"
        pr = "CAD $2,199.99"
        tags = '["LG","MD-Only"]'
    elif product_id.startswith(("WM", "WT")):
        dv = "MS"
        cat = "Appliance"
        sub = "Washer"
        ico = "👕"
        pr = "CAD $1,299.99"
        tags = '["LG","MD-Only"]'
    else:
        return None

    nm = metadata.get("name", product_id)
    url = metadata.get("url", "")
    op = "Canada"

    # Escape markdown
    md_escaped = escape_for_javascript(md_content)
    analysis_escaped = escape_for_javascript(analysis_content)

    # Build object code as single line
    code = (
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
        f'mdAnalysis:`{analysis_escaped}`,'
        f'md:`{md_escaped}`'
        f'}}'
    )

    return code

def main():
    v6_20_file = Path("C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html")

    if not v6_20_file.exists():
        print("[ERROR] v6_20.html not found")
        return False

    # Read file
    content = v6_20_file.read_text(encoding='utf-8')

    print("[STEP 1] Checking current state...")
    initial_count = content.count('id:"')
    print(f"[INFO] Initial product count: {initial_count}")

    # Step 1: Remove the incorrectly placed products (lines ~5818+)
    # Look for the pattern where products were wrongly inserted in function code
    # Find all product object definitions that appear after the const P array closes (line 1735)

    # Find the position of const P=[...];
    const_p_start = content.find('const P=[')
    if const_p_start < 0:
        print("[ERROR] Could not find const P array start")
        return False

    # Find the closing ];  for const P
    bracket_count = 0
    in_string = False
    escape_next = False
    const_p_end = -1

    for i in range(const_p_start + len('const P=[') - 1, len(content)):
        c = content[i]

        if escape_next:
            escape_next = False
            continue

        if c == '\\':
            escape_next = True
            continue

        if c in ('"', "'", '`'):
            in_string = not in_string
            continue

        if not in_string:
            if c == '[':
                bracket_count += 1
            elif c == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    # Found the closing ]
                    const_p_end = i + 2  # Include the ];
                    break

    if const_p_end < 0:
        print("[ERROR] Could not find const P array closing bracket")
        return False

    print(f"[INFO] Found const P array: lines start to {const_p_end}")

    # Now remove any stray product definitions that appear after the const P array
    # Look for pattern: },\n{ or ,\n{ that appear after const_p_end and contain id:"
    after_array = content[const_p_end:]

    # Find and remove improperly placed product objects
    # Pattern: {id:"...",... followed by backtick content
    bad_products_pattern = r',\{id:"(OLED55C5PUA|OLED77C5PUA|OLED83C5PUA|LF25S6560S|LF30S8210S|LF29S8365S|LF25Z6211S|LK14S8000V|WM6700HBA|WM8900HBA|WT8600CB)"[^}]*`[^`]*`[^}]*\}'

    # More precise: find each product's full definition including md field
    # This is complex, so let's use a different approach: remove everything that looks like an inserted product

    print("[STEP 2] Removing incorrectly placed products from outside const P array...")

    # Find all the bad product definitions - they start with {id:" and contain mdAnalysis and md template literals
    # The simplest approach: find each product by its id pattern

    products_to_remove = [
        "OLED55C5PUA",
        "OLED77C5PUA",
        "OLED83C5PUA",
        "LF25S6560S",
        "LF30S8210S",
        "LF29S8365S",
        "LF25Z6211S",
        "LK14S8000V",
        "WM6700HBA",
        "WM8900HBA",
        "WT8600CB",
    ]

    for product_id in products_to_remove:
        # Find all occurrences of this product
        pattern = f'{{id:"{product_id}",[^{{}}]*md:`[^`]*`'
        matches = list(re.finditer(pattern, content, re.DOTALL))

        # Remove from end to start (to preserve positions)
        for match in reversed(matches):
            match_start = match.start()
            match_end = match.end()

            # Only remove if it's outside the const P array
            if match_start > const_p_end:
                print(f"  [REMOVING] {product_id} at position {match_start}")
                content = content[:match_start] + content[match_end:]

    print("[STEP 3] Generating proper product code for 11 missing products...")
    missing_products = [
        "OLED55C5PUA",
        "OLED77C5PUA",
        "OLED83C5PUA",
        "LF25S6560S",
        "LF30S8210S",
        "LF29S8365S",
        "LF25Z6211S",
        "LK14S8000V",
        "WM6700HBA",
        "WM8900HBA",
        "WT8600CB",
    ]

    product_codes = []
    for product_id in missing_products:
        code = create_product_code(product_id)
        if code:
            product_codes.append(code)
            print(f"  [OK] {product_id}")
        else:
            print(f"  [FAIL] {product_id}")

    if not product_codes:
        print("[ERROR] No products generated")
        return False

    print("[STEP 4] Inserting products into const P array...")

    # Recalculate const_p_end since content has changed
    const_p_match = re.search(r'const P=\[(.+?)\];', content, re.DOTALL)
    if not const_p_match:
        print("[ERROR] Could not find const P array after cleanup")
        return False

    # Find the position right before the closing ];
    insert_pos = content.rfind('];')
    if insert_pos < 0:
        print("[ERROR] Could not find ];")
        return False

    # Check if there are multiple ]; (const P closes, then other code)
    # We need the FIRST ]; that closes the const P array
    # Better approach: find }]; which closes the const P

    # Search from the beginning for "const P=[" then find the matching "];"
    const_p_start_pos = content.find('const P=[')
    bracket_depth = 0
    in_string = False
    string_char = None
    escape_next = False

    for i in range(const_p_start_pos + 8, len(content)):
        c = content[i]

        if escape_next:
            escape_next = False
            continue

        if c == '\\':
            escape_next = True
            continue

        if not in_string:
            if c in ('"', "'", '`'):
                in_string = True
                string_char = c
            elif c == '{':
                bracket_depth += 1
            elif c == '}':
                bracket_depth -= 1
            elif c == '[':
                bracket_depth += 1
            elif c == ']':
                bracket_depth -= 1
                # Check if next char is ;
                if i + 1 < len(content) and content[i + 1] == ';' and bracket_depth == -1:
                    insert_pos = i
                    break
        else:
            if c == string_char:
                in_string = False

    if insert_pos < 0:
        print("[ERROR] Could not find const P array closing")
        return False

    # Build new products section
    new_product_section = "," + ",".join(product_codes)

    # Insert before the closing ];
    before = content[:insert_pos]
    after = content[insert_pos:]

    new_content = before + new_product_section + after

    # Write back
    v6_20_file.write_text(new_content, encoding='utf-8')

    print("[STEP 5] Verification...")
    final_count = new_content.count('id:"')
    print(f"  Initial products: {initial_count}")
    print(f"  Final products: {final_count}")
    print(f"  Added: {final_count - initial_count}")

    print(f"\n[SUCCESS] Fixed const P array integration!")
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
