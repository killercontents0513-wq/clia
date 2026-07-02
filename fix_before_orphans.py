#!/usr/bin/env python3
"""Remove orphaned products from before-array section (inside _embedBlobUrl function)"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')
const_p_pos = content.find('const P=[')

# Show exact context around the orphan block start and end
first_orphan_pos = content.find('{id:"OLED55C5PUA"', 0, const_p_pos)
print(f'First before-orphan at: {first_orphan_pos:,}')
print(f'Context 30 before: {repr(content[first_orphan_pos-30:first_orphan_pos])}')

# Find where the orphan block ENDS (before const P=[)
# Walk from first_orphan_pos, tracking depth
j = first_orphan_pos
in_str=False; sc=''; escaped=False; depth=0; last_end=-1
while j < const_p_pos + 200:  # a little past const P
    c = content[j]
    if escaped: escaped=False; j+=1; continue
    if c=='\\': escaped=True; j+=1; continue
    if in_str:
        if c==sc: in_str=False
    else:
        if c in ('"',"'",'`'): in_str=True; sc=c
        elif c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0:
                # Check if next product follows
                rest = content[j+1:j+15].lstrip(',\n ')
                if rest.startswith('{id:"'):
                    last_end = j+1
                else:
                    last_end = j+1
                    break
    j+=1

print(f'Orphan block ends at: {last_end:,}')
print(f'Context 30 after: {repr(content[last_end:last_end+50])}')
print(f'Orphan block size: {last_end - first_orphan_pos:,} chars')
print()

# The removal: cut from first_orphan_pos to last_end
# But need to handle leading comma: what's immediately before first_orphan_pos?
# Context: "...new Blob([arr{id:..." -> no comma before {
# Just remove the products, leaving "...new Blob([arr]..."
before_orphan = content[:first_orphan_pos]
after_orphan = content[last_end:]

# Remove any leading comma before the orphan
if before_orphan.rstrip('\n ').endswith(','):
    before_orphan = before_orphan.rstrip('\n ')
    before_orphan = before_orphan[:-1]  # remove the comma
    print(f'Removed leading comma')

new_content = before_orphan + after_orphan
print(f'New file: {len(new_content):,} chars (was {len(content):,})')

# Count products
total = new_content.count('id:"')
new_const_p = new_content.find('const P=[')
i2 = new_const_p + 9
depth2=1; in_str2=False; sc2=''; escaped2=False; end2=-1
while i2 < len(new_content):
    c2 = new_content[i2]
    if escaped2: escaped2=False; i2+=1; continue
    if c2=='\\': escaped2=True; i2+=1; continue
    if in_str2:
        if c2==sc2: in_str2=False
    else:
        if c2 in ('"',"'",'`'): in_str2=True; sc2=c2
        elif c2=='[': depth2+=1
        elif c2==']':
            depth2-=1
            if depth2==0: end2=i2; break
    i2+=1

in_arr = new_content[new_const_p:end2+2].count('id:"')
print(f'In const P: {in_arr}, total: {total}, orphaned: {total-in_arr}')

if 'function renderList' not in new_content:
    print('ERROR: renderList missing!')
elif 'function _embedBlobUrl' not in new_content:
    print('ERROR: _embedBlobUrl missing!')
else:
    Path('LG_AI_Content_Hub_v6_20.html').write_text(new_content, encoding='utf-8')
    print('[SUCCESS] Saved.')
