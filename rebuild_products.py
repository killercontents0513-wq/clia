#!/usr/bin/env python3
"""
sp:{},md:`CONTENT`},tags: 구조를 sp:{},tags:로 수정하고
올바른 위치의 md 필드를 최신 파일 내용으로 업데이트
"""
import sys, io, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

def escape_for_js(text):
    if not text: return ""
    text = text.replace('\\', '\\\\')
    text = text.replace('\r', '')
    text = text.replace('\n', '\\n')
    text = text.replace('\t', '\\t')
    text = text.replace('`', '\\`')
    text = text.replace('$', '\\$')
    return text

def read_backtick_value(s, start):
    """s[start]이 ` 다음 문자일 때, 닫는 backtick 위치 반환"""
    i = start
    esc = False
    while i < len(s):
        c = s[i]
        if esc: esc=False; i+=1; continue
        if c == '\\': esc=True; i+=1; continue
        if c == '`': return i
        i+=1
    return -1

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

products = [
    'OLED65C5PUA','OLED77C5PUA',
    'OLED55C5PUA','OLED83C5PUA',
    'LF25S6560S','LF30S8210S','LF29S8365S','LF25Z6211S',
    'LK14S8000V','WM6700HBA','WM8900HBA','WT8600CB'
]

base_dir = Path('MD-ONLY-LIST')

for pid in products:
    print(f"\n[FIX] {pid}")

    # 최신 md 내용 읽기
    md_file = base_dir / f"{pid.lower()}-product-info.md"
    if not md_file.exists():
        print(f"  [SKIP] md file missing"); continue
    new_md = escape_for_js(md_file.read_text(encoding='utf-8'))

    # 제품 위치 찾기
    pid_pattern = f'id:"{pid}"'
    idx = content.find(pid_pattern)
    if idx < 0:
        print(f"  [SKIP] product not in file"); continue

    # sp:{} 위치 찾기
    sp_pos = content.find('sp:{},', idx)
    if sp_pos < 0 or sp_pos > idx + 5000:
        sp_pos = content.find('sp:{},', idx)
        print(f"  sp:{{}}, not found near {idx}"); continue

    # sp:{} 바로 다음 확인
    after_sp = content[sp_pos+6:sp_pos+10]
    print(f"  after sp:{{}},: {repr(after_sp)}")

    if content[sp_pos+6:sp_pos+9] == 'md:':
        # 잘못된 md 필드가 sp 이후에 있음
        # sp:{},md:`...`}, 패턴에서 `...` 제거
        md_bt_start = sp_pos + 6 + 3  # 'md:' 다음 backtick
        if content[md_bt_start] != '`':
            print(f"  [WARN] Expected backtick, got {repr(content[md_bt_start])}"); continue

        md_bt_end = read_backtick_value(content, md_bt_start + 1)
        if md_bt_end < 0:
            print(f"  [ERROR] Cannot find end of bad md field"); continue

        # md_bt_end 이후 },  확인
        after_md = content[md_bt_end+1:md_bt_end+3]
        print(f"  after bad md: {repr(after_md)}")

        if after_md[0] == '}':
            # sp:{},md:`...`}, 부분을 sp:{}, 로 교체
            bad_section = content[sp_pos:md_bt_end+2]  # sp:{},md:`...`}
            print(f"  Removing bad section ({len(bad_section):,} chars)")
            content = content[:sp_pos] + 'sp:{},' + content[md_bt_end+2:]
            print(f"  Bad md removed from sp position")
            # 위치 재계산
            idx = content.find(pid_pattern)
        else:
            print(f"  [WARN] Unexpected char after md field: {repr(after_md)}")
    else:
        print(f"  No bad md at sp position (OK)")

    # 이제 올바른 위치의 md 필드 업데이트 (mdAnalysis 이후)
    # 제품 오브젝트 내에서 md: 필드 찾기 (마지막 것)
    search_from = idx
    # mdAnalysis 이후에 있는 md: 찾기
    mda_pos = content.find('mdAnalysis:`', search_from)
    if mda_pos < 0 or mda_pos > search_from + 600000:
        print(f"  [WARN] mdAnalysis not found near product"); continue

    mda_end_bt = read_backtick_value(content, mda_pos + 12)
    if mda_end_bt < 0:
        print(f"  [ERROR] Cannot find end of mdAnalysis"); continue

    # mdAnalysis 이후 md: 찾기
    after_mda = content[mda_end_bt+1:mda_end_bt+10]
    print(f"  After mdAnalysis: {repr(after_mda)}")

    if content[mda_end_bt+1:mda_end_bt+4] == ',md':
        # 기존 md 필드가 있음 - 업데이트
        md_pos = mda_end_bt + 1
        md_bt_start = md_pos + 4  # ',md:`' -> backtick position
        if content[md_bt_start] != '`':
            print(f"  [WARN] Expected backtick at md, got {repr(content[md_bt_start])}"); continue
        md_bt_end = read_backtick_value(content, md_bt_start + 1)
        if md_bt_end < 0:
            print(f"  [ERROR] Cannot find end of md field"); continue

        old_md = content[md_bt_start+1:md_bt_end]
        print(f"  Replacing md field ({len(old_md):,} chars → {len(new_md):,} chars)")
        content = content[:md_bt_start+1] + new_md + content[md_bt_end:]
        print(f"  md field updated")
    else:
        # md 필드 없음 - 추가
        print(f"  Adding md field after mdAnalysis")
        insert_pos = mda_end_bt + 1
        content = content[:insert_pos] + f',md:`{new_md}`' + content[insert_pos:]
        print(f"  md field added")

# 저장
print()
print("Saving file...")
# Node.js 파싱 테스트
script3_start = 106461 + len('<script>')
script3_end = content.rfind('</script>', 106461, 2100000)
script_js = content[script3_start:script3_end]
Path('_test_script.js').write_text(script_js, encoding='utf-8')
result = subprocess.run(['node', '--input-type=module'],
                       input=script_js.encode('utf-8'),
                       capture_output=True, timeout=30)
if result.returncode == 0:
    print("[OK] Node.js parse: NO ERRORS")
else:
    err = result.stderr.decode('utf-8', errors='replace')
    print("[ERROR] Parse errors remain:")
    for line in err.split('\n')[:8]:
        print(f"  {line}")

Path('LG_AI_Content_Hub_v6_20.html').write_text(content, encoding='utf-8')
print(f"Saved: {len(content):,} chars")
