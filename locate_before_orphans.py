#!/usr/bin/env python3
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

const_p_pos = content.find('const P=[')
before = content[:const_p_pos]
print(f'Before-array length: {len(before):,} (const P at {const_p_pos:,})')

# Find all orphan product IDs in before-array
for m in re.finditer(r'id:"([^"]+)"', before):
    pid = m.group(1)
    pos = m.start()
    # Show context: 100 before, 150 after
    ctx = before[max(0,pos-100):pos+150]
    print(f'\n--- {pid} at pos {pos:,} ---')
    print(ctx.encode('ascii','replace').decode('ascii'))

# Also check if these are inside a string literal (base64/JSON data)
print('\n--- Checking if orphans are inside string literals ---')
# Walk the before section and track string state
in_str = False; sc=''; escaped=False
str_ranges = []
cur_start = -1
i = 0
while i < len(before):
    c = before[i]
    if escaped: escaped=False; i+=1; continue
    if c=='\\': escaped=True; i+=1; continue
    if in_str:
        if c==sc:
            in_str=False
            if sc=='"' and i-cur_start > 10000:  # large string
                str_ranges.append((cur_start, i))
    else:
        if c in ('"',"'",'`'): in_str=True; sc=c; cur_start=i
    i+=1

print(f'Large string literals in before-array: {len(str_ranges)}')
for s,e in str_ranges:
    print(f'  String {s:,}-{e:,} ({e-s:,} chars): starts with {repr(before[s:s+30])}')
    # Check if any orphan is inside this string
    for m in re.finditer(r'id:"([^"]+)"', before[s:e]):
        print(f'    => Contains orphan: {m.group(1)} at offset {m.start():,}')
