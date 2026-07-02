"""
v6_20 제품 리스트 순서 재배치 유틸
- 지정 코드들을 배열 맨 앞으로 이동 (순서 유지)
"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

V6_20 = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'

# 맨 앞에 올 제품 (앞→뒤 순서)
TOP_ORDER = ['RH10V9PV2W', 'WFV1214BST1']

html = open(V6_20, encoding='utf-8').read()

# 배열 범위 찾기
first_id  = html.find('{id:"')
arr_open  = html.rfind('[', 0, first_id)
arr_close = html.find('];', first_id)
before    = html[:arr_open + 1]
after     = html[arr_close:]
arr_body  = html[arr_open + 1:arr_close]

# 개별 엔트리 분리 (각 엔트리는 {id:"...",...} 형태)
# 엔트리 경계: {id:" 로 시작
splits = list(re.finditer(r'(?=\{id:")', arr_body))
entries = []
for i, m in enumerate(splits):
    start = m.start()
    end   = splits[i+1].start() if i+1 < len(splits) else len(arr_body)
    raw   = arr_body[start:end].rstrip(',\n ')
    code_m = re.match(r'\{id:"([^"]+)"', raw)
    code  = code_m.group(1) if code_m else f'UNKNOWN_{i}'
    entries.append((code, raw))

print(f'Total entries: {len(entries)}')
print('Before:', [c for c, _ in entries[:5]])

# TOP_ORDER 엔트리 추출 + 나머지
top_entries  = []
rest_entries = []
top_codes    = set(TOP_ORDER)
code_map     = {c: e for c, e in entries}

for code in TOP_ORDER:
    if code in code_map:
        top_entries.append((code, code_map[code]))
    else:
        print(f'WARNING: {code} not found')

for code, entry in entries:
    if code not in top_codes:
        rest_entries.append((code, entry))

new_entries = top_entries + rest_entries
print('After :', [c for c, _ in new_entries[:5]])

# 배열 재조합
new_body = ',\n'.join(e for _, e in new_entries)
new_html = before + '\n' + new_body + '\n' + after

with open(V6_20, 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f'\n✅ Reordered: {len(new_entries)} entries')
print(f'   Top: {[c for c,_ in new_entries[:3]]}')
