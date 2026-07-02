#!/usr/bin/env python3
"""P 배열의 마지막 제품들과 구조 확인"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

# P 배열 추출
def find_p_bounds(content):
    start = content.find('const P=[')
    if start < 0: return -1,-1
    i = start + 8  # position of '['
    depth = 0
    in_str = False; sc = ''; esc = False
    while i < len(content):
        c = content[i]
        if esc: esc=False; i+=1; continue
        if c == '\\': esc=True; i+=1; continue
        if in_str:
            if c == sc: in_str=False
        else:
            if c in ('"',"'",'`'): in_str=True; sc=c
            elif c == '[': depth+=1
            elif c == ']':
                depth-=1
                if depth==0: return start, i
        i+=1
    return -1,-1

arr_start, arr_end = find_p_bounds(content)
arr = content[arr_start:arr_end+1]
print(f"P array: {arr_start:,} to {arr_end:,} ({len(arr):,} chars)")
print()

# 새로 추가한 제품들 확인
new_prods = ['OLED55C5PUA','OLED83C5PUA','LF25S6560S','LF30S8210S',
             'LF29S8365S','LF25Z6211S','LK14S8000V','WM6700HBA','WM8900HBA','WT8600CB']

for pid in new_prods:
    idx = arr.find(f'id:"{pid}"')
    if idx < 0:
        print(f"{pid}: NOT FOUND"); continue

    # md 필드 시작 찾기
    obj_region = arr[idx:idx+50000]
    md_idx = obj_region.find('md:`')
    if md_idx < 0:
        print(f"{pid}: NO md field"); continue

    md_val_start = md_idx + 4
    # 첫 번째 unescaped backtick 찾기 (md 필드 끝)
    j = md_val_start
    esc2 = False
    while j < len(obj_region):
        c = obj_region[j]
        if esc2: esc2=False; j+=1; continue
        if c == '\\': esc2=True; j+=1; continue
        if c == '`':
            md_end = j
            break
        j+=1
    else:
        print(f"{pid}: md field UNCLOSED!"); continue

    md_size = md_end - md_val_start
    # md 값의 첫 50자 확인 (unescape)
    md_preview = obj_region[md_val_start:md_val_start+80].replace('\\n','\n').replace('\\`','`')
    print(f"{pid}: md OK ({md_size:,} chars) | starts: {md_preview[:50].encode('ascii','replace').decode('ascii')!r}")

    # ${} 가 있는지 확인 (unescaped)
    md_raw = obj_region[md_val_start:md_end]
    dollar_template = [i for i in range(len(md_raw)-1)
                       if md_raw[i] == '$' and md_raw[i+1] == '{' and
                       (i == 0 or md_raw[i-1] != '\\')]
    if dollar_template:
        print(f"  WARNING: Unescaped ${{ at positions {dollar_template[:5]}")
    # 연속 backtick 확인
    if '``' in md_raw:
        print(f"  WARNING: Double backtick found!")

print()
# 배열 끝 부분 확인
print("Array tail (last 200 chars):")
print(repr(arr[-200:]))
print()
print(f"Char immediately after array: {repr(content[arr_end+1:arr_end+10])}")
