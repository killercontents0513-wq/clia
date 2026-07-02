#!/usr/bin/env python3
"""sp:{,md: -> sp:{},md: 수정"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

html = Path('LG_AI_Content_Hub_v6_20.html')
content = html.read_text(encoding='utf-8')

before = content.count('sp:{,')
print(f"Before: {before} occurrences of 'sp:{{,'")

# 수정: sp:{, -> sp:{},
fixed = content.replace('sp:{,', 'sp:{},')

after = fixed.count('sp:{,')
fixed_count = fixed.count('sp:{},') - content.count('sp:{},')
print(f"After:  {after} occurrences of 'sp:{{,' (should be 0)")
print(f"Fixed:  {before - after} replacements made")

# 검증: P array 파싱 테스트
if 'sp:{,' in fixed:
    print("[ERROR] Still has sp:{, pattern!")
    exit(1)

# renderList 확인
if 'function renderList' not in fixed:
    print("[ERROR] renderList missing!")
    exit(1)

print()
print("Running Node.js parse test...")

# JS 블록만 추출해서 node.js로 테스트
import subprocess
script3_start = 106461 + len('<script>')
script3_end = 2064355
script_js = fixed[script3_start:script3_end]
Path('_test_script.js').write_text(script_js, encoding='utf-8')

result = subprocess.run(['node', '--input-type=module'],
                       input=script_js.encode('utf-8'),
                       capture_output=True, timeout=30)
if result.returncode == 0:
    print("[OK] Node.js parse: NO ERRORS")
    html.write_text(fixed, encoding='utf-8')
    print(f"[SAVED] File written: {len(fixed):,} chars")
else:
    err = result.stderr.decode('utf-8', errors='replace')
    # 첫 번째 오류만 출력
    lines = err.split('\n')
    for i, line in enumerate(lines[:15]):
        print(line)
    print()
    print("[WARNING] Still has parse errors. Saving anyway to check...")
    html.write_text(fixed, encoding='utf-8')
    print(f"[SAVED] File written: {len(fixed):,} chars")
