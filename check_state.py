#!/usr/bin/env python3
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')
cp = content.find('const P=[')
print(f'File: {len(content):,} chars')
print(f'const P=[ at {cp:,}')
print(f'Before (100 chars): {repr(content[cp-100:cp])}')
print(f'Start (100 chars): {repr(content[cp:cp+100])}')

# Find closing ] using bracket+string tracking
i = cp + 9
depth = 1; in_str=False; sc=''; escaped=False; end=-1
while i < len(content):
    c = content[i]
    if escaped: escaped=False; i+=1; continue
    if c == chr(92): escaped=True; i+=1; continue
    if in_str:
        if c == sc: in_str=False
    else:
        if c in ('"', "'", '`'): in_str=True; sc=c
        elif c == '[': depth+=1
        elif c == ']':
            depth-=1
            if depth==0: end=i; break
    i+=1

print(f'Array closes at {end:,}')
print(f'Context at close: {repr(content[end-50:end+50])}')
print(f'id count in array: {content[cp:end+2].count("id:")}')
print(f'id count total: {content.count("id:\"")}')

# Check for anything after array before renderList
after_array = content[end+2:]
rl = after_array.find('function renderList')
print(f'renderList chars after array: {rl:,}')

# Check for orphan products after array
import re
orph = re.findall(r'id:"([^"]+)"', after_array[:rl] if rl > 0 else after_array[:500000])
print(f'Orphaned ids before renderList: {orph[:10]}')

# Check script structure
scripts = [(m.start(), content[m.start():m.start()+60]) for m in re.finditer(r'</script>', content, re.IGNORECASE)]
print(f'\n</script> tags:')
for pos, ctx in scripts:
    print(f'  {pos:,}: {repr(ctx[:60])}')
