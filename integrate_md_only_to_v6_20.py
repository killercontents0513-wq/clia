#!/usr/bin/env python3
"""
MD-Only 제품을 v6_20.html에 통합
"""
import json
import re
from pathlib import Path

# 12개 우선순위 제품
PRIORITY_12 = [
    "OLED55C5PUA", "OLED65C5PUA", "OLED77C5PUA", "OLED83C5PUA",
    "LF25S6560S", "LF30S8210S", "LF29S8365S", "LF25Z6211S", "LK14S8000V",
    "WM6700HBA", "WM8900HBA", "WT8600CB"
]

def read_md_file(code):
    """MD 파일 읽기"""
    md_file = Path(f"C:/Users/Administrator/Desktop/AI/RetailOBS/3P/MD-ONLY-LIST/{code.lower()}-product-info.md")
    if md_file.exists():
        return md_file.read_text(encoding='utf-8')
    return None

def create_product_entry(code, md_content):
    """제품 엔트리 생성"""
    # MD 내용을 JavaScript 문자열로 변환
    md_escaped = md_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

    # 간단한 제품 엔트리 생성
    entry = f'{{id:"{code}",dv:"MS",cat:"TV",sub:"OLED",ico:"📺",nm:"LG {code}",pr:"TBD",url:"https://www.lg.com/ca_en/",crawled:false,gal:[],feat:[],sp:{{}},md:"{md_escaped}",md Only:true}}'

    return entry

def main():
    v6_20_file = Path("C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html")

    if not v6_20_file.exists():
        print("[ERROR] v6_20.html not found")
        return

    # 12개 제품 읽기
    products_to_add = []
    for code in PRIORITY_12:
        md_content = read_md_file(code)
        if md_content:
            entry = create_product_entry(code, md_content)
            products_to_add.append((code, entry))
            print(f"[OK] {code} - MD loaded ({len(md_content)} chars)")
        else:
            print(f"[SKIP] {code} - MD file not found")

    print(f"\n[READY] {len(products_to_add)} products ready for integration")
    print("[NEXT] Update v6_20.html const P array manually or use JavaScript integration")

if __name__ == '__main__':
    main()
