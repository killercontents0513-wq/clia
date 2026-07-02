#!/usr/bin/env python3
"""Find exactly where the corruption is"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

# Script 3 starts at 106,469 (after <script>)
script_start = 106469
local_pos = 1544304
full_pos = script_start + local_pos

print(f"Unclosed template literal at full file pos: {full_pos:,}")
print()

# Show 500 chars around this position
ctx = content[full_pos-200:full_pos+800]
print("=== Context (400 before to 800 after) ===")
print(ctx.encode('ascii', 'replace').decode('ascii'))
print()

# Find all backticks in a range around this position to understand nesting
region = content[full_pos-5000:full_pos+5000]
bt_positions = [i for i, c in enumerate(region) if c == '`']
print(f"Backtick positions (relative) in ±5000 range: {bt_positions[:30]}")

# Check: what is the content right at that position
print(f"\nChar at full_pos: {repr(content[full_pos])}")
print(f"Content at full_pos±10: {repr(content[full_pos-10:full_pos+10])}")
