#!/usr/bin/env python3
"""Surgically remove the orphaned product block from the after-array section"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

# Find const P bounds
start = content.find('const P=[')
i = start + 9
depth = 1; in_str=False; sc=''; escaped=False; end=-1
while i < len(content):
    c = content[i]
    if escaped: escaped=False; i+=1; continue
    if c=='\\': escaped=True; i+=1; continue
    if in_str:
        if c==sc: in_str=False
    else:
        if c in ('"',"'",'`'): in_str=True; sc=c
        elif c=='[': depth+=1
        elif c==']':
            depth-=1
            if depth==0: end=i; break
    i+=1

array_end_pos = end + 2  # position after ];
after = content[array_end_pos:]

# Find where orphaned block starts (first orphaned id: that is OUTSIDE const P array)
# OLED55C5PUA is the first orphan in after-array
# Look for the pattern just before it
orphan_start_in_after = after.find('{id:"OLED55C5PUA"')
if orphan_start_in_after < 0:
    # Try to find any orphan
    for pid in ['OLED65C5PUA','OLED77C5PUA','OLED83C5PUA']:
        pos = after.find(f'{{id:"{pid}"')
        if pos >= 0:
            orphan_start_in_after = pos
            break

print(f"First orphan block starts at after-pos: {orphan_start_in_after:,}")
print(f"Context before orphan: {repr(after[max(0,orphan_start_in_after-50):orphan_start_in_after+30])}")

# Walk from the orphan start to find where all orphans end
# The last orphan should be WT8600CB - find its closing backtick
# Products end with md:`...`} - need to find the last closing `}
j = orphan_start_in_after
in_str = False; sc=''; escaped=False; brace_depth=0
last_good_end = j

while j < len(after):
    c = after[j]
    if escaped: escaped=False; j+=1; continue
    if c=='\\': escaped=True; j+=1; continue
    if in_str:
        if c==sc: in_str=False
    else:
        if c in ('"',"'",'`'): in_str=True; sc=c
        elif c=='{': brace_depth+=1
        elif c=='}':
            brace_depth-=1
            if brace_depth==0:
                last_good_end = j+1
                # Check: is the next char a ',' followed by another '{id:"'?
                rest = after[j+1:j+10].lstrip(',\n ')
                if rest.startswith('{id:"'):
                    # More products follow - continue
                    pass
                else:
                    # No more products
                    break
    j+=1

print(f"Orphan block ends at after-pos: {last_good_end:,}")
print(f"Context after orphan: {repr(after[last_good_end:last_good_end+100])}")

# Determine what to remove
# We need to also remove the leading comma if present
remove_start = orphan_start_in_after
# Check if there's a comma before the orphan block
pre = after[max(0,orphan_start_in_after-5):orphan_start_in_after]
if pre.rstrip('\n ').endswith(','):
    # Include the comma in removal
    comma_pos = after.rfind(',', 0, orphan_start_in_after)
    if comma_pos >= orphan_start_in_after - 5:
        remove_start = comma_pos

remove_end = last_good_end

print(f"\nRemoving after-array chars {remove_start:,} to {remove_end:,} ({remove_end-remove_start:,} chars)")

# Build new content
new_after = after[:remove_start] + after[remove_end:]
new_content = content[:array_end_pos] + new_after

# Verify
total = new_content.count('id:"')
in_arr = new_content[start:end+2].count('id:"')
print(f"\nAfter removal: {in_arr} in array, {total} total, {total-in_arr} orphaned")

if 'function renderList' not in new_content:
    print('ERROR: renderList missing!')
else:
    Path('LG_AI_Content_Hub_v6_20.html').write_text(new_content, encoding='utf-8')
    print(f'[SUCCESS] Saved. File: {len(new_content):,} chars')
