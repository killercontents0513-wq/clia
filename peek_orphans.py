#!/usr/bin/env python3
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

after = content[end+2:]
print(f'After-array length: {len(after):,}')

# Find id:" occurrences in after
for m in re.finditer(r'id:"([^"]+)"', after):
    pid = m.group(1)
    pos = m.start()
    # Show 50 chars before and 200 after
    ctx = after[max(0,pos-30):pos+200]
    print(f'\n--- {pid} at after-pos {pos:,} ---')
    print(ctx.encode('ascii','replace').decode('ascii'))
