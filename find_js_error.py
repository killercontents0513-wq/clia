#!/usr/bin/env python3
"""Find where the JS syntax error is by scanning the script content"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

# Script 3: 106,461 to 1,931,084
script_start = 106461 + len('<script>')  # skip the tag itself
script_end = 1931084
script = content[script_start:script_end]

print(f"Script 3 content length: {len(script):,} chars")
print(f"const P=[ local pos: {script.find('const P=['):,}")
print()

# Walk through script tracking string state
# Report where each md:` backtick template starts and ends
in_str = False
sc = ''
escaped = False
depth = 0
template_stack = []
errors = []

i = 0
bt_count = 0

while i < len(script):
    c = script[i]

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
            in_str = False
            sc = ''
    else:
        if c == '`':
            in_str = True
            sc = '`'
            bt_count += 1
            if bt_count % 2 == 1:  # Opening backtick
                template_stack.append(i)
            else:  # Closing backtick
                if template_stack:
                    open_pos = template_stack.pop()
                    # Report very large template literals (potential issues)
                    size = i - open_pos
                    if size > 50000:
                        # Get context
                        label_start = max(0, open_pos - 30)
                        label = script[label_start:open_pos+20].encode('ascii','replace').decode('ascii')
                        print(f"LARGE template literal: pos {open_pos:,}-{i:,} ({size:,} chars)")
                        print(f"  starts: {label}")
        elif c in ('"', "'"):
            in_str = True
            sc = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1

    i += 1

print(f"Unclosed template literals: {len(template_stack)}")
for pos in template_stack:
    label = script[max(0,pos-50):pos+50].encode('ascii','replace').decode('ascii')
    print(f"  at local pos {pos:,}: {label}")

print(f"Final depth: {depth} (should be 0)")

# Look for </script> inside the script
inner_close = list(re.finditer(r'</script', script, re.IGNORECASE))
print(f"\n</script> occurrences inside script 3: {len(inner_close)}")
for m in inner_close:
    ctx = script[max(0,m.start()-50):m.start()+30].encode('ascii','replace').decode('ascii')
    print(f"  at {m.start():,}: {ctx}")

# Check later scripts (5 and 6) for function P
for tag_range, label in [((1939066, 2001448), 'Script 5'), ((2004310, 2027430), 'Script 6')]:
    s, e = tag_range
    block = content[s:e]
    # Search for P definitions
    p_defs = re.findall(r'(?:function P|const P|var P|let P)[^a-zA-Z]', block)
    if p_defs:
        print(f"\n{label} defines P: {p_defs}")
    else:
        print(f"\n{label}: no P definitions")
    # First 200 chars
    print(f"  First 200: {block[:200].encode('ascii','replace').decode('ascii')}")
