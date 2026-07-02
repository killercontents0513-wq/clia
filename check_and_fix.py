#!/usr/bin/env python3
"""Check what's in const P array and fix it properly"""
import json
from pathlib import Path

content = open('LG_AI_Content_Hub_v6_20.html', encoding='utf-8').read()

# Find const P array boundaries
start_idx = content.find('const P=[')
i = start_idx + 9
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
                end_idx = i
                break
    i += 1

array_content = content[start_idx:end_idx+2]
print(f'Array range: {start_idx} to {end_idx}')
print(f'Array length: {end_idx - start_idx} chars')

# Count products in array
import re
ids_in_array = re.findall(r'id:"([^"]+)"', array_content)
print(f'Products in const P: {len(ids_in_array)}')

# Check for our 12 priority products
priority = ['OLED55C5PUA','OLED65C5PUA','OLED77C5PUA','OLED83C5PUA',
            'LF25S6560S','LF30S8210S','LF29S8365S','LF25Z6211S','LK14S8000V',
            'WM6700HBA','WM8900HBA','WT8600CB']
for p in priority:
    print(f'  {p}: {"IN ARRAY" if p in ids_in_array else "MISSING"}')

# Find all occurrences of each priority product in ENTIRE file
print('\n--- All occurrences in full file ---')
for p in ['OLED77C5PUA']:
    all_pos = [m.start() for m in re.finditer(f'id:"{p}"', content)]
    for pos in all_pos:
        in_range = start_idx < pos < end_idx
        print(f'{p} at {pos}: {"IN ARRAY" if in_range else "OUTSIDE"}')
