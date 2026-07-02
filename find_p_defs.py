#!/usr/bin/env python3
"""Find ALL definitions of P in the HTML file"""
from pathlib import Path
import re

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

# Find ALL occurrences where P is assigned or defined
patterns = [
    r'const P\s*=',
    r'var P\s*=',
    r'let P\s*=',
    r'function P\s*\(',
    r'P\s*=\s*function',
    r'window\.P\s*=',
]

for pat in patterns:
    for m in re.finditer(pat, content):
        pos = m.start()
        print(f"[{pat}] at {pos}: {repr(content[pos:pos+80])}")

# Also check if the const P=[...] block is syntactically isolated
# by checking script tag boundaries
script_starts = [m.start() for m in re.finditer(r'<script[^>]*>', content)]
script_ends = [m.start() for m in re.finditer(r'</script>', content)]

const_p_pos = content.find('const P=[')
print(f'\nconst P=[ at position: {const_p_pos}')

# Which script block contains it?
containing_script = None
for s in script_starts:
    # Find the next </script> after this <script>
    end_candidates = [e for e in script_ends if e > s]
    if not end_candidates:
        continue
    e = min(end_candidates)
    if s < const_p_pos < e:
        containing_script = (s, e)
        print(f'Containing <script> block: {s} to {e} (length: {e-s:,})')
        break

# Check if there's a syntax error BEFORE const P in the same script block
if containing_script:
    s, e = containing_script
    script_content = content[s:e]
    const_p_local = script_content.find('const P=[')

    # Look at what comes just before const P in this script
    before_p = script_content[:const_p_local]
    print(f'\nScript block: {len(script_content):,} chars')
    print(f'Content before const P: {len(before_p):,} chars')

    # Check for syntax issues - are there unclosed template literals?
    # Count backticks
    bt_count = before_p.count('`')
    print(f'Backticks before const P in script: {bt_count} ({"EVEN - OK" if bt_count % 2 == 0 else "ODD - PROBLEM!"})')

    # Check for any obvious issues
    print(f'\nLast 500 chars before const P=[')
    print(repr(before_p[-500:]))
