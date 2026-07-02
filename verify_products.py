#!/usr/bin/env python3
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

# Find const P array
start = content.find('const P=[')
if start < 0:
    print("const P not found")
    exit(1)

i = start + 9
depth = 1
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
                array_end = i
                break
    i += 1

array_content = content[start:array_end+1]

print("=== PRODUCT VERIFICATION ===\n")

# Find both products
for product_id in ['OLED65C5PUA', 'OLED77C5PUA']:
    pattern = f'id:"{product_id}"'
    idx = array_content.find(pattern)
    if idx >= 0:
        # Extract context around this product
        context_start = max(0, idx - 100)
        context_end = min(len(array_content), idx + 1000)
        context = array_content[context_start:context_end]

        # Check if md field exists
        md_start = context.find('md:`')
        if md_start >= 0:
            print(f"✓ {product_id}: md field FOUND")
            # Get a preview of markdown content
            md_preview = context[md_start:md_start+300]
            # Check for standardized structure
            if '# LG OLED' in md_preview:
                print(f"  ✓ Contains # title (standardized)")
            if '## Product Overview' in md_preview:
                print(f"  ✓ Contains ## sections (standardized)")
            if '### ' in md_preview:
                print(f"  ✓ Contains ### subsections (standardized)")
            print()
        else:
            print(f"✗ {product_id}: md field NOT FOUND")
            print()
    else:
        print(f"✗ {product_id}: NOT FOUND in array")
        print()

print(f"Total products in array: {array_content.count('id:\"')}")
