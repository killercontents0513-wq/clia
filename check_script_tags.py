#!/usr/bin/env python3
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

# Find all script tags
scripts = list(re.finditer(r'<script([^>]*)>', content, re.IGNORECASE))
ends = list(re.finditer(r'</script>', content, re.IGNORECASE))

print(f"Total <script> tags: {len(scripts)}")
print(f"Total </script> tags: {len(ends)}")
print()

const_p_pos = content.find('const P=[')
print(f"const P=[ at: {const_p_pos:,}")
print()

for i, s in enumerate(scripts):
    # Find matching end
    matching_ends = [e for e in ends if e.start() > s.start()]
    if matching_ends:
        e = matching_ends[0]
        contains_p = s.start() < const_p_pos < e.start()
        attrs = s.group(1).strip()
        print(f"Script {i+1}: {s.start():,} to {e.start():,} | attrs='{attrs}' | contains_const_P={contains_p}")
    else:
        print(f"Script {i+1}: {s.start():,} (NO CLOSING TAG)")

print()
# Check the main script block's first 200 chars
main_script = None
for s in scripts:
    matching_ends = [e for e in ends if e.start() > s.start()]
    if matching_ends:
        e = matching_ends[0]
        if s.start() < const_p_pos < e.start():
            main_script = (s.start(), e.start(), s.group(1))
            break

if main_script:
    s_pos, e_pos, attrs = main_script
    block = content[s_pos:e_pos]
    print(f"Main script block: {s_pos:,} to {e_pos:,}, {len(block):,} chars, attrs='{attrs}'")
    print(f"First 300 chars of script content:")
    print(repr(block[len('<script' + attrs + '>'):len('<script' + attrs + '>')+300]))
    print()

    # Check backtick count in entire script block BEFORE const P
    const_p_local = content.find('const P=[') - s_pos
    before_p = block[:const_p_local + len('<script' + attrs + '>')]
    bt_before = before_p.count('`')
    print(f"Backticks before const P in this script: {bt_before} ({'EVEN-OK' if bt_before%2==0 else 'ODD-PROBLEM'})")

    # Find any unclosed template literals
    in_template = False
    template_depth = 0
    for idx, c in enumerate(before_p):
        if c == '\\':
            continue
        if c == '`':
            in_template = not in_template
    print(f"Template literal still open at const P: {in_template}")
