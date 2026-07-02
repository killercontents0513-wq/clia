#!/usr/bin/env python3
"""
Fix missing 11 MD-Only products - Version 2
"""
import re
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
    """Read markdown file for product"""
    md_file = Path(f"C:/Users/Administrator/Desktop/AI/RetailOBS/3P/MD-ONLY-LIST/{product_id.lower()}-product-info.md")
    if md_file.exists():
        return md_file.read_text(encoding='utf-8')
    return ""

def read_analysis_file(product_id):
    """Read analysis file for product"""
    analysis_file = Path(f"C:/Users/Administrator/Desktop/AI/RetailOBS/3P/MD-ONLY-LIST/{product_id.upper()}-MD-ANALYSIS.md")
    if analysis_file.exists():
        return analysis_file.read_text(encoding='utf-8')
    return ""

def read_metadata(product_id):
    """Read metadata JSON for product"""
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
    elif product_id.startswith(("LF", "LK")):
        dv = "MS"
        cat = "Appliance"
        sub = "Refrigerator" if "LF" in product_id else "Kimchi Refrigerator"
        ico = "🧊"
        pr = "CAD $3,999.99"
    elif product_id.startswith(("WM", "WT")):
        dv = "MS"
        cat = "Appliance"
        sub = "Washer"
        ico = "👕"
        pr = "CAD $1,299.99"
    else:
        return None

    nm = metadata.get("name", product_id)
    url = metadata.get("url", "")
    op = "Canada"

    # Escape markdown
    md_escaped = escape_for_javascript(md_content)
    analysis_escaped = escape_for_javascript(analysis_content)

    # Build object code
    code = "{"
    code += f'id:"{product_id}",'
    code += f'dv:"{dv}",'
    code += f'cat:"{cat}",'
    code += f'sub:"{sub}",'
    code += f'ico:"{ico}",'
    code += f'nm:"{nm}",'
    code += f'pr:"{pr}",'
    code += f'op:"{op}",'
    code += f'url:"{url}",'
    code += f'crawled:false,'
    code += f'gal:[],'
    code += f'feat:[],'
    code += f'sp:' + json.dumps({}) + ','
    code += f'tags:["OLED" if "OLED" in "{product_id}" else "LG","MD-Only"],' if "OLED" in product_id else f'tags:["LG","MD-Only"],'
    code += f'bul:[],'
    code += f'kw:"{nm}",'
    code += f'mdAnalysis:`{analysis_escaped}`,'
    code += f'md:`{md_escaped}`'
    code += "}"

    return code

def main():
    v6_20_file = Path("C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html")

    if not v6_20_file.exists():
        print("[ERROR] v6_20.html not found")
        return False

    # Read file
    content = v6_20_file.read_text(encoding='utf-8')

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
            print(f"    [OK] {product_id} ready")
        else:
            print(f"    [FAIL] {product_id}")

    # Find insertion point: right before ];
    # Pattern: look for the LAST occurrence of }\n]; which closes the const P array
    insertion_pattern = r'\}\n\];'

    # Find all matches
    matches = list(re.finditer(insertion_pattern, content))
    if not matches:
        print("[ERROR] Could not find const P array closing bracket")
        return False

    # Get the first match (should be line 1735)
    match = matches[0]
    insert_pos = match.start()

    # Get what comes before the closing bracket
    before_close = content[:insert_pos]
    after_close = content[insert_pos:]

    # Build new products section
    new_product_section = "," + ",".join(product_codes)

    # Build new content
    new_content = before_close + new_product_section + after_close

    # Write back
    v6_20_file.write_text(new_content, encoding='utf-8')

    print(f"\n[SUCCESS] Integrated 11 missing MD-Only products into const P array")
    print(f"  - OLED TVs: OLED55C5PUA, OLED77C5PUA, OLED83C5PUA")
    print(f"  - Refrigerators: LF25S6560S, LF30S8210S, LF29S8365S, LF25Z6211S, LK14S8000V")
    print(f"  - Washers: WM6700HBA, WM8900HBA, WT8600CB")

    # Verify
    product_count = len(re.findall(r'id:"', new_content))
    print(f"  Total products in const P: {product_count}")

    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
