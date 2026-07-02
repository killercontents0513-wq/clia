#!/usr/bin/env python3
"""현재 파일에서 OLED65C5PUA 주변 100자씩 확인"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

# P 배열 찾기
arr_start = content.find('const P=[')
arr_end = content.rfind('];', arr_start, arr_start+2000000)
arr = content[arr_start:arr_end+2]

# OLED65C5PUA 주변 구조 파악
idx = arr.find('id:"OLED65C5PUA"')
# sp: 필드 찾기
sp_idx = arr.find('sp:', idx)
print(f"sp: context (200 chars after sp:):")
print(arr[sp_idx:sp_idx+200].encode('ascii','replace').decode('ascii'))
print()

# tags: 필드 찾기
tags_idx = arr.find(',tags:', idx)
print(f"Before tags: (50 chars):")
print(arr[tags_idx-50:tags_idx+20].encode('ascii','replace').decode('ascii'))
print()

# mdAnalysis 필드 끝 확인
mda_idx = arr.find('mdAnalysis:`', idx)
print(f"mdAnalysis starts at relative pos: {mda_idx}")
# mdAnalysis 값 끝 찾기
j = mda_idx + 12
esc = False
while j < len(arr):
    c = arr[j]
    if esc: esc=False; j+=1; continue
    if c == '\\': esc=True; j+=1; continue
    if c == '`': break
    j+=1
print(f"mdAnalysis ends at relative pos: {j}")
print(f"After mdAnalysis (100 chars): {arr[j:j+100].encode('ascii','replace').decode('ascii')}")
print()

# 제품 오브젝트 실제 끝 찾기 (배열 안에서 ,{ 패턴)
next_prod = arr.find(',{id:', idx+10)
if next_prod < 0:
    next_prod = arr.find(']', idx)
print(f"Next product/array-end at: {next_prod}")
print(f"Content between mdAnalysis end and next product ({j} to {next_prod}):")
print(arr[j:next_prod].encode('ascii','replace').decode('ascii'))
