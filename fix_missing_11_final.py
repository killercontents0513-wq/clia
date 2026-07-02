#!/usr/bin/env python3
"""
Integrate 11 missing MD-Only products - Final Version
Uses simple string replacement
"""
import json
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

    # Check current state
    initial_count = content.count('id:"')
    print(f"[INFO] Initial product count: {initial_count}")

    # List of 11 missing products
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

    print("[INFO] Generating code for 11 missing products...")
    product_codes = []

    for product_id in missing_products:
        print(f"  Processing {product_id}...")
        code = create_product_code(product_id)
        if code:
            product_codes.append(code)
            print(f"    [OK] {product_id}")
        else:
            print(f"    [FAIL] {product_id}")

    # Build new products section: comma + products
    new_product_section = "," + ",".join(product_codes)

    # Find and replace the closing bracket pattern
    # Look for: }]; (closing of last product + closing of array)
    # Replace with: },newproducts...}];

    # Use simple string replacement - look for the const P closing
    closing_pattern = "}];"

    if closing_pattern not in content:
        print("[ERROR] Could not find const P closing pattern")
        return False

    # Find the LAST occurrence (to get the const P array, not other arrays)
    last_index = content.rfind(closing_pattern)

    # Split content
    before = content[:last_index]
    after = content[last_index:]

    # Insert the new products before the closing
    new_content = before + new_product_section + after

    # Write back
    v6_20_file.write_text(new_content, encoding='utf-8')

    # Verify
    final_count = new_content.count('id:"')
    print(f"\n[SUCCESS] Integration complete!")
    print(f"  Initial products: {initial_count}")
    print(f"  Final products: {final_count}")
    print(f"  Products added: {final_count - initial_count}")
    print(f"  Expected to add: 11")

    if final_count - initial_count == 11:
        print(f"\n[VERIFIED] All 11 products successfully integrated!")
        return True
    else:
        print(f"\n[WARNING] Product count mismatch!")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
