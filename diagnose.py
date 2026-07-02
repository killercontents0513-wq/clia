#!/usr/bin/env python3
"""Diagnose JS parse error in const P array"""
from pathlib import Path
import re

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

# Find const P bounds
start = content.find('const P=[')
i = start + 9
depth = 1
in_str = False; sc = ''; escaped = False; end = -1
while i < len(content):
    c = content[i]
    if escaped: escaped=False; i+=1; continue
    if c == '\\': escaped=True; i+=1; continue
    if in_str:
        if c == sc: in_str=False
    else:
        if c in ('"', "'", '`'): in_str=True; sc=c
        elif c == '[': depth+=1
        elif c == ']':
            depth-=1
            if depth==0: end=i; break
    i+=1

print(f'Array: {start} to {end}, length: {end-start:,}')
array = content[start:end+2]

# Check OLED77C5PUA entry
idx = array.find('id:"OLED77C5PUA"')
if idx >= 0:
    # Find the md:` field
    md_start = array.find('md:`', idx)
    if md_start >= 0:
        # Find the matching closing backtick
        j = md_start + 4
        while j < len(array):
            if array[j] == '\\':
                j += 2
                continue
            if array[j] == '`':
                print(f"md field: chars {md_start} to {j}, length: {j-md_start:,}")
                # Check for raw (unescaped) backticks or $ inside
                md_content = array[md_start+4:j]
                raw_backtick = md_content.count('`')
                raw_dollar = md_content.count('${')
                print(f"  Raw backticks inside md: {raw_backtick}")
                print(f"  Raw template expressions ${{: {raw_dollar}")
                if raw_backtick > 0:
                    # Find first raw backtick
                    pos = md_content.find('`')
                    print(f"  First raw backtick at offset {pos}:")
                    print(f"  Context: {repr(md_content[max(0,pos-50):pos+50])}")
                break
            j += 1

# Also check mdAnalysis field
mdA_start = array.find('mdAnalysis:`', idx)
if mdA_start >= 0:
    j = mdA_start + 12
    while j < len(array):
        if array[j] == '\\':
            j += 2
            continue
        if array[j] == '`':
            content_inner = array[mdA_start+12:j]
            raw_bt = content_inner.count('`')
            print(f"mdAnalysis field length: {j-mdA_start:,}, raw backticks: {raw_bt}")
            if raw_bt > 0:
                pos = content_inner.find('`')
                print(f"  Context: {repr(content_inner[max(0,pos-50):pos+50])}")
            break
        j += 1

# Look for any unescaped backticks inside ALL md/mdAnalysis fields
print("\n--- Checking ALL products for unescaped backticks ---")
problems = []
for m in re.finditer(r'id:"([^"]+)"', array):
    pid = m.group(1)
    entry_start = m.start()
    # Find md:` for this entry
    md_pos = array.find('md:`', entry_start)
    if md_pos < 0:
        continue
    # Find next entry or end
    next_entry = array.find('{id:"', entry_start + 1)
    if next_entry < 0:
        next_entry = len(array)

    j = md_pos + 4
    while j < min(len(array), next_entry + 1000):
        if array[j] == '\\':
            j += 2
            continue
        if array[j] == '`':
            inner = array[md_pos+4:j]
            bt = inner.count('`')
            if bt > 0:
                problems.append((pid, bt, inner.find('`')))
            break
        j += 1

if problems:
    print(f"PROBLEMS FOUND: {len(problems)} products with unescaped backticks")
    for pid, count, pos in problems:
        print(f"  {pid}: {count} unescaped backtick(s)")
else:
    print("No unescaped backtick issues found in md fields")

# Check the actual JS - look for the part where const P is defined
# Check if the array starts correctly
print(f"\nArray start: {repr(array[:50])}")
print(f"Array end:   {repr(array[-50:])}")
