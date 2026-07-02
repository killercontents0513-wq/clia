#!/usr/bin/env python3
"""JS 파싱 오류 위치 정확히 찾기"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

# Script 태그 위치 찾기
script_starts = [m.start() for m in re.finditer(r'<script[^>]*>', content, re.IGNORECASE)]
script_ends   = [m.start() for m in re.finditer(r'</script>', content, re.IGNORECASE)]
print(f"<script>  tags: {len(script_starts)} at {script_starts}")
print(f"</script> tags: {len(script_ends)}  at {script_ends}")
print()

# const P=[ 위치
p_pos = content.find('const P=[')
print(f"const P=[ at: {p_pos:,}")
print()

# 메인 스크립트 찾기 (const P 포함하는 것)
for i, s in enumerate(script_starts):
    ends_after = [e for e in script_ends if e > s]
    if not ends_after:
        print(f"Script {i+1}: starts at {s:,}, NO END TAG")
        continue
    e = ends_after[0]
    contains_p = s < p_pos < e if p_pos > 0 else False
    tag_end = content.find('>', s)
    attrs = content[s:tag_end+1]
    print(f"Script {i+1}: {s:,} -> {e:,} | contains_P={contains_p} | {attrs[:60]}")

print()
# 메인 스크립트 블록 추출 (const P 포함)
main_s = None
for i, s in enumerate(script_starts):
    ends_after = [e for e in script_ends if e > s]
    if ends_after and s < p_pos < ends_after[0]:
        main_s = s
        main_e = ends_after[0]
        break

if main_s is None:
    print("ERROR: Cannot find main script block containing const P")
    # const P 앞의 script 시작 찾기
    for s in reversed([x for x in script_starts if x < p_pos]):
        main_s = s
        ends_after = [e for e in script_ends if e > s]
        main_e = ends_after[0] if ends_after else len(content)
        print(f"Fallback: using script at {s:,}")
        break

if main_s:
    script_block = content[main_s:main_e]
    print(f"Main script block: {main_s:,} to {main_e:,} ({len(script_block):,} chars)")
    print()

    # const P 위치 (블록 내 상대 위치)
    local_p = script_block.find('const P=[')
    print(f"const P=[ local pos: {local_p:,}")
    print()

    # 블록 내 template literal 검사
    # const P 앞까지 backtick 홀짝 확인
    before_p = script_block[:local_p] if local_p >= 0 else script_block[:5000]
    bt_count = 0
    in_str = False
    in_single = False
    in_double = False
    escaped = False
    unclosed_bt = []

    for idx, c in enumerate(before_p):
        if escaped:
            escaped = False
            continue
        if c == '\\':
            escaped = True
            continue
        if in_str:
            if in_single and c == "'": in_str = False; in_single = False
            elif in_double and c == '"': in_str = False; in_double = False
        else:
            if c == '"':  in_str = True; in_double = True
            elif c == "'": in_str = True; in_single = True
            elif c == '`':
                bt_count += 1
                if bt_count % 2 == 1:  # opening
                    unclosed_bt.append(idx)
                else:  # closing
                    if unclosed_bt: unclosed_bt.pop()

    print(f"Backtick count before const P: {bt_count} ({'EVEN-OK' if bt_count%2==0 else 'ODD - PROBLEM!'})")
    if unclosed_bt:
        print(f"Unclosed backticks before const P at local positions: {unclosed_bt[:5]}")
        for pos in unclosed_bt[:3]:
            ctx = script_block[max(0,pos-100):pos+200]
            print(f"\n--- Unclosed backtick at local pos {pos:,} (full pos {main_s+pos:,}) ---")
            print(ctx.encode('ascii', 'replace').decode('ascii'))
    else:
        print("No unclosed backticks before const P (good)")

    # P 배열 끝 확인
    if local_p >= 0:
        i = main_s + local_p + 9
        depth = 1
        in_str2 = False
        sc2 = ''
        esc2 = False
        while i < len(content) and i < main_s + local_p + 5000000:
            c = content[i]
            if esc2: esc2=False; i+=1; continue
            if c == '\\': esc2=True; i+=1; continue
            if in_str2:
                if c == sc2: in_str2=False
            else:
                if c in ('"',"'",'`'): in_str2=True; sc2=c
                elif c == '[': depth+=1
                elif c == ']':
                    depth-=1
                    if depth==0:
                        print(f"\nP array ends at full pos: {i:,}")
                        break
            i+=1
        else:
            print(f"\nP array UNCLOSED (depth={depth} after scanning)")
