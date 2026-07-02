#!/usr/bin/env python3
"""Check what's around const P= in the file"""
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')
idx = content.find('const P=[')
print('Position of const P=[:', idx)
print()

# What's in the 300 chars before it
before = content[idx-300:idx]
print('=== 300 chars BEFORE const P=[ ===')
print(before.encode('ascii', errors='replace').decode('ascii'))
print()

# What comes after the array closes
start = idx
i = idx + 9
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

after = content[end+2:end+400]
print('=== 400 chars AFTER const P closes ===')
print(after.encode('ascii', errors='replace').decode('ascii'))

# Check if there's a <script> tag that contains const P
# Find which script tag contains const P
script_start = content.rfind('<script', 0, idx)
script_end_before = content.rfind('</script>', 0, idx)
print(f'\nNearest <script> before const P: position {script_start}')
print(f'Nearest </script> before const P: position {script_end_before}')
if script_start > script_end_before:
    print('=> const P is INSIDE a <script> block (correct)')
else:
    print('=> const P is OUTSIDE any <script> block (WRONG!)')

# Look for function P definitions
import re
func_p = list(re.finditer(r'function\s+P\s*\(', content))
print(f'\nfunction P() definitions: {len(func_p)}')
for m in func_p:
    print(f'  at {m.start()}: {repr(content[m.start():m.start()+50])}')
