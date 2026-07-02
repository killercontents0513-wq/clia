#!/usr/bin/env python3
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

# Find ALL </script> positions
ends = [m.start() for m in re.finditer(r'</script>', content, re.IGNORECASE)]
starts = [m.start() for m in re.finditer(r'<script[^>]*>', content, re.IGNORECASE)]

print(f"<script> positions: {starts}")
print(f"</script> positions: {ends}")
print()

# Find the rogue <script> at 1,524,449
rogue_pos = 1524449
print(f"Context at {rogue_pos}:")
ctx = content[rogue_pos-200:rogue_pos+300]
print(ctx.encode('ascii','replace').decode('ascii'))
print()

# Check: does the HTML browser see the script block ending before const P=[?
# The browser will end the <script> block at the first </script> after it opens
# Script 3 starts at 106,461
# What is the ACTUAL first </script> after 106,461?
script3_start = 106461
first_end_after_script3 = min(e for e in ends if e > script3_start)
print(f"Script 3 starts at: {script3_start:,}")
print(f"First </script> after script 3: {first_end_after_script3:,}")
print(f"const P=[ is at: {content.find('const P=['):,}")

if first_end_after_script3 < content.find('const P=['):
    print("*** PROBLEM: </script> closes BEFORE const P=[ - P array is OUTSIDE script block! ***")
else:
    print("Script 3 contains const P=[ (OK)")

# Also show what's around that first </script>
print(f"\nContext around </script> at {first_end_after_script3}:")
ctx2 = content[first_end_after_script3-100:first_end_after_script3+100]
print(ctx2.encode('ascii','replace').decode('ascii'))
