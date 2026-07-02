#!/usr/bin/env python3
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

p_start = 1011191
p_end   = 1609172
array_content = content[p_start:p_end+1]
print(f"Array: {len(array_content):,} chars, {array_content.count('id:\"'):} products")
print()

# Script 4 at 1,657,720
rogue = 1657720
print(f"Script 4 tag at {rogue:,}:")
print(repr(content[rogue:rogue+120]))
print()

# What's between P array end and Script 4
between = content[p_end+1:rogue]
print(f"Between P end and Script4 ({len(between):,} chars):")
print(repr(between[:400]))
print()

# Check the JS between p_end and next </script>
# to find any template literals or syntax issues
script3_end = 2064355
after_p = content[p_end+1:script3_end]
print(f"Content right after P array (first 500 chars):")
print(after_p[:500].encode('ascii','replace').decode('ascii'))
print()

# Check all products have proper md field
# by scanning the full JS block for template literal balance
script3_content = content[106461:script3_end]
print(f"Script 3 length: {len(script3_content):,}")

# Find unclosed template literals in entire Script 3
in_str = False
sc = ''
escaped = False
depth = 0
open_templates = []

i = 0
while i < len(script3_content):
    c = script3_content[i]
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
            if sc == '`':
                if open_templates:
                    open_templates.pop()
            in_str = False
    else:
        if c == '`':
            in_str = True
            sc = '`'
            open_templates.append(i)
        elif c in ('"', "'"):
            in_str = True
            sc = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
    i += 1

print(f"Unclosed template literals: {len(open_templates)}")
for pos in open_templates[:5]:
    full_pos = 106461 + pos
    ctx = script3_content[max(0,pos-80):pos+100]
    print(f"  At local {pos:,} (full {full_pos:,}):")
    print(f"  {ctx.encode('ascii','replace').decode('ascii')}")
    print()
print(f"Final brace depth: {depth}")
