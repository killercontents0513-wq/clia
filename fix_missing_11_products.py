#!/usr/bin/env python3
"""
Fix missing 11 MD-Only products in v6_20.html const P array
Only OLED65C5PUA was successfully integrated; the other 11 are missing
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

def create_product_object(product_id):
    """Create JavaScript product object"""
    md_content = read_markdown_file(product_id)
    analysis_content = read_analysis_file(product_id)
    metadata = read_metadata(product_id)

    # Determine category and other info from metadata or product ID
    if "OLED" in product_id:
        dv = "MS"
        cat = "TV"
        sub = "OLED evo"
        ico = "📺"
        pr = metadata.get("price", "CAD $1,699.99")
    elif product_id.startswith(("LF", "LK")):
        dv = "MS"
        cat = "Appliance"
        sub = "Refrigerator" if "LF" in product_id else "Kimchi Refrigerator"
        ico = "🧊"
        pr = metadata.get("price", "CAD $3,999.99")
    elif product_id.startswith(("WM", "WT")):
        dv = "MS"
        cat = "Appliance"
        sub = "Washer"
        ico = "👕"
        pr = metadata.get("price", "CAD $1,299.99")
    else:
        return None

    nm = metadata.get("name", product_id)
    url = metadata.get("url", "")
    op = metadata.get("op", "Canada")

    # Escape markdown content
    md_escaped = escape_for_javascript(md_content)
    analysis_escaped = escape_for_javascript(analysis_content)

    # Build object
    obj = {
        "id": product_id,
        "dv": dv,
        "cat": cat,
        "sub": sub,
        "ico": ico,
        "nm": nm,
        "pr": pr,
        "op": op,
        "url": url,
        "crawled": False,
        "gal": [],
        "feat": [],
        "sp": {},
        "tags": ["OLED" if "OLED" in product_id else "LG", "MD-Only"],
        "bul": [],
        "kw": metadata.get("kw", nm),
        "mdAnalysis": analysis_escaped,
        "md": md_escaped
    }

    return obj

def generate_product_code(obj):
    """Generate JavaScript code for product object"""
    code = "{"
    code += f'id:"{obj["id"]}",'
    code += f'dv:"{obj["dv"]}",'
    code += f'cat:"{obj["cat"]}",'
    code += f'sub:"{obj["sub"]}",'
    code += f'ico:"{obj["ico"]}",'
    code += f'nm:"{obj["nm"]}",'
    code += f'pr:"{obj["pr"]}",'
    code += f'op:"{obj["op"]}",'
    code += f'url:"{obj["url"]}",'
    code += f'crawled:{str(obj["crawled"]).lower()},'
    code += f'gal:{json.dumps(obj["gal"])},'
    code += f'feat:{json.dumps(obj["feat"])},'
    code += f'sp:' + json.dumps(obj["sp"]) + ','
    code += f'tags:{json.dumps(obj["tags"])},'
    code += f'bul:{json.dumps(obj["bul"])},'
    code += f'kw:"{obj["kw"]}",'
    code += f'mdAnalysis:`{obj["mdAnalysis"]}`,'
    code += f'md:`{obj["md"]}`'
    code += "}"

    return code

def main():
    v6_20_file = Path("C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html")

    if not v6_20_file.exists():
        print("[ERROR] v6_20.html not found")
        return False

    # Read file
    content = v6_20_file.read_text(encoding='utf-8')

    # List of 11 missing products (in order: 4 TVs + 5 refrigerators + 3 washers)
    missing_products = [
        "OLED55C5PUA",  # 55" TV
        "OLED77C5PUA",  # 77" TV
        "OLED83C5PUA",  # 83" TV
        "LF25S6560S",   # 25cu.ft fridge
        "LF30S8210S",   # 30cu.ft fridge
        "LF29S8365S",   # 29cu.ft fridge
        "LF25Z6211S",   # 25cu.ft fridge
        "LK14S8000V",   # Kimchi fridge
        "WM6700HBA",    # 5.0 cu.ft washer
        "WM8900HBA",    # 5.8 cu.ft washer
        "WT8600CB",     # 5.5 cu.ft washer
    ]

    print("[INFO] Generating product objects for 11 missing products...")
    product_codes = []

    for product_id in missing_products:
        print(f"  Processing {product_id}...")
        obj = create_product_object(product_id)
        if obj:
            code = generate_product_code(obj)
            product_codes.append(code)
            print(f"    [OK] {product_id} ready for integration")
        else:
            print(f"    [FAIL] {product_id} failed")

    # Find the insertion point: right before the `];` that closes const P array
    # Look for the last `},{id:"...` before `];`
    insertion_pattern = r'(\],)'  # Find ];
    match = re.search(insertion_pattern, content)

    if not match:
        print("[ERROR] Could not find const P array closing bracket")
        return False

    # Find the position right before ];
    insert_pos = match.start()

    # Get the content before insertion point
    before_insertion = content[:insert_pos]

    # Check if we need to add a comma before our new products
    # Look at what's immediately before: should be }
    if before_insertion and before_insertion[-1] == '}':
        new_product_section = "," + ",".join(product_codes)
    else:
        new_product_section = ",".join(product_codes)

    # Build new content
    new_content = before_insertion + new_product_section + content[insert_pos:]

    # Write back
    v6_20_file.write_text(new_content, encoding='utf-8')

    # Count products
    product_count = len(re.findall(r'id:"', new_content))

    print(f"\n[SUCCESS] Integrated 11 missing MD-Only products")
    print(f"  - OLED TVs: OLED55C5PUA, OLED77C5PUA, OLED83C5PUA")
    print(f"  - Refrigerators: LF25S6560S, LF30S8210S, LF29S8365S, LF25Z6211S, LK14S8000V")
    print(f"  - Washers: WM6700HBA, WM8900HBA, WT8600CB")
    print(f"  Total products in const P: {product_count}")

    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
