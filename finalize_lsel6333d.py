"""
LSEL6333D 재크롤 (v2)
- 갤러리: STS-01-01~04 + STS-05 + STS-06 (6장 제품 외관)
- 피처: STS-02/03/07/08/09-01/09-02/09-03 (7장 desktop) — 헤드라인을 페이지 H2 실제 텍스트로 정렬
- 스펙: 페이지 keyFeatureList (6개) 기반 + 카테고리 표준 22개 필드로 확장
"""
import re, sys, io, struct, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

V6_20    = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
CODE     = 'LSEL6333D'
CDN_BASE = 'https://www.lg.com/content/dam/channel/wcms/sa_en'

TOP_ORDER = ['LSEL6333D', 'LT19HBHSIN', 'S90TR', 'S80TR', 'S45TR', '32GS95UV-B', 'WTV17HHD', '27US550-W', 'WK1310BST', 'RH10V9PV2W', 'WFV1214BST1']

# ── 갤러리: 진짜 제품 사진 large01~15 (LG 내부코드 MD07581414 폴더) ────
# 참고: 폴더명이 /microwaves/ 이지만 LG CMS 의 내부 product ID 매핑상 LSEL6333D 의 갤러리임
# (data-bv-product-id="MD07581414" 로 페이지에서 확인됨)
GAL_BASE = '/images/microwaves/md07581414/gallery/'
GAL_PATHS = [GAL_BASE + f'large{str(i).zfill(2)}.jpg' for i in range(1, 16)]

# 피처 이미지는 별도 BASE
BASE = '/images/ha/'

# ── 피처: STS-02/03/07/08/09 (7장) — 헤드라인을 페이지 H2 텍스트와 정렬 ─
# Source: H2/H3 elements near each STS image on actual LG.com page
FEAT_LIST = [
    (BASE + 'HA-Slide-Oven-Range-LSEL6333D-STS-02-desktop.jpg',
     'Large capacity', 'Large Capacity — 6.3 cu ft Oven',
     'Spacious 6.3 cu ft oven holds large dishes and feeds the whole family with room to spare.'),
    (BASE + 'HA-Slide-Oven-Range-LSEL6333D-STS-03-desktop.jpg',
     'EasyClean', 'The Easy Way to Keep Your Oven Clean',
     'EasyClean® removes light soils in just 10 minutes with water — no harsh chemicals or high heat.'),
    (BASE + 'HA-Slide-Oven-Range-LSEL6333D-STS-07-desktop.jpg',
     '2-in-1 Design', 'Experience Smarter Cooking with 2-in-1 Design',
     'Combination cooktop and oven design optimized for everyday home cooking and family meals.'),
    (BASE + 'HA-Slide-Oven-Range-LSEL6333D-STS-08-desktop.jpg',
     'A Sleek Look', 'Sleek Slide-in Design',
     'Slide-in installation with no rear backguard — gives you a built-in, cabinet-flush look.'),
    (BASE + 'HA-Slide-Oven-Range-LSEL6333D-STS-09-01-desktop.jpg',
     'Smart ThinQ', 'Smart Control with LG ThinQ',
     'Control your oven remotely, get cooking notifications and start preheating from the ThinQ app.'),
    (BASE + 'HA-Slide-Oven-Range-LSEL6333D-STS-09-02-desktop.jpg',
     'Air Fry', 'Feed a Crowd with Delicious Air Fry Flavor',
     'Built-in Air Fry delivers crispy results with little to no oil, right in your oven.'),
    (BASE + 'HA-Slide-Oven-Range-LSEL6333D-STS-09-03-desktop.jpg',
     'Dual Element', '9/12" Dual Radiant Cooktop Element',
     'The dual radiant element adapts to your cookware size — efficient heat for any pot or pan.'),
]

# ── 스펙: keyFeatureList (6개) 기반 + 카테고리 표준 18 필드 확장 ──────
SPECS = {
    'Type':                'Slide-in Electric Range',
    'Oven_Capacity':       '6.3 cu ft',
    'Cooktop_Type':         'Smoothtop / Glass-Ceramic',
    'Cooktop_Elements':    '5 (incl. Dual 9/12 inch Element)',
    'Dual_Element':        'Yes (9/12 inch Radiant)',
    'Fuel_Type':           'Electric',
    'Fan_Convection':      'Yes',
    'Air_Fry':             'Yes (Built-in)',
    'EasyClean':           'Yes (10-min, Low Heat)',
    'Self_Clean':          'Yes (High Heat)',
    'Wide_View_Window':    'Yes',
    'Oven_Light':          'Yes',
    'Smart_ThinQ_WiFi':    'Yes',
    'ThinQ_Care':          'Yes',
    'Voice_Control':       'Google Assistant / Alexa',
    'Controls':            'Glass Touch + Front Tilt Knobs',
    'Storage_Drawer':      'Yes (Built-in)',
    'Installation':        'Slide-in (no rear backguard)',
    'Finish':              'Stainless Steel',
    'Color':               'Stainless Steel',
    'Model':               CODE,
}

# ── 유틸 ───────────────────────────────────────────────────────────────
def jsstr(s):
    if s is None: s = ''
    s = str(s).replace('\u2122', 'TM').replace('\u00ae', 'R').replace('\u2019', "'")
    s = s.replace('\\', '\\\\').replace('"', '\\"')
    return re.sub(r'\s+', ' ', s.replace('\n', ' ').replace('\r', '').replace('\t', ' ')).strip()

def image_dims(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'Range': 'bytes=0-65536', 'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=15).read()
            if data[:2] == b'\xff\xd8':
                i = 2
                while i < len(data) - 9:
                    if data[i] != 0xff: break
                    mk = data[i+1]; ln = struct.unpack('>H', data[i+2:i+4])[0]
                    if mk in (0xC0, 0xC2):
                        return struct.unpack('>H', data[i+7:i+9])[0], struct.unpack('>H', data[i+5:i+7])[0]
                    i += 2 + ln
            if data[:8] == b'\x89PNG\r\n\x1a\n':
                return struct.unpack('>II', data[16:24])
        except Exception:
            if attempt < retries - 1: time.sleep(1)
    return 0, 0

def replace_field(entry, field, new_val):
    pat = re.compile(r'(?<=[,{])\s*' + re.escape(field) + r'\s*:\s*(\[[\s\S]*?\]|\{[\s\S]*?\})', re.DOTALL)
    m = pat.search(entry)
    if not m: print(f'  WARNING: {field} not found'); return entry
    return entry[:m.start(1)] + new_val + entry[m.end(1):]

def replace_str_field(entry, field, new_val):
    pat = re.compile(r'(?<=[,{])' + re.escape(field) + r':"(?:[^"\\]|\\.)*"')
    m = pat.search(entry)
    if not m: print(f'  WARNING: str {field} not found'); return entry
    return entry[:m.start()] + f'{field}:"{new_val}"' + entry[m.end():]

# ── 치수 순차 fetch ────────────────────────────────────────────────────
print('Fetching dimensions...')
all_paths = GAL_PATHS + [p for p, *_ in FEAT_LIST]
dims = {}
for p in all_paths:
    url = CDN_BASE + p
    w, h = image_dims(url)
    dims[p] = (w, h)
    print(f'  {p.split("/")[-1]}: {w}x{h}')
    time.sleep(0.1)

# ── JS 빌드 ───────────────────────────────────────────────────────────
print('\nBuilding JS...')
gal_parts = [f'{{a:"View {i}",p:"{p}",w:{dims.get(p,(0,0))[0]},h:{dims.get(p,(0,0))[1]}}}'
             for i, p in enumerate(GAL_PATHS, 1)]
new_gal_js = '[' + ','.join(gal_parts) + ']'
feat_parts = [f'{{a:"{jsstr(a)}",p:"{p}",t:"{jsstr(t)}",d:"{jsstr(d)}",w:{dims.get(p,(0,0))[0]},h:{dims.get(p,(0,0))[1]}}}'
              for p, a, t, d in FEAT_LIST]
new_feat_js = '[' + ','.join(feat_parts) + ']'
sp_parts = [f'"{k}":"{jsstr(v)}"' for k, v in SPECS.items()]
new_sp_js = '{' + ','.join(sp_parts) + '}'
print(f'  gal:{len(gal_parts)} feat:{len(feat_parts)} sp:{len(sp_parts)}')

# ── v6_20 교체 ────────────────────────────────────────────────────────
print('\nUpdating v6_20...')
v620 = open(V6_20, encoding='utf-8').read()
idx = v620.find(f'{{id:"{CODE}"')
if idx < 0: print('ERROR'); sys.exit(1)
nxt = v620.find('{id:"', idx + 10)
entry_old = v620[idx:nxt]
print(f'  Old: {len(entry_old):,} chars')
entry_new = replace_field(entry_old, 'gal', new_gal_js)
entry_new = replace_field(entry_new, 'feat', new_feat_js)
entry_new = replace_field(entry_new, 'sp', new_sp_js)
entry_new = replace_str_field(entry_new, 'nm', 'LG 6.3 cu ft Electric Range with Air Fry & ThinQ')
entry_new = replace_str_field(entry_new, 'pr', '5199')
print(f'  New: {len(entry_new):,} chars')
v620_new = v620[:idx] + entry_new + v620[nxt:]
open(V6_20, 'w', encoding='utf-8').write(v620_new)
print('  Saved.')

# ── 순서 재배치 ────────────────────────────────────────────────────────
print('\nReordering...')
html2 = open(V6_20, encoding='utf-8').read()
fi = html2.find('{id:"'); ao = html2.rfind('[', 0, fi); ac = html2.find('];', fi)
before, after, body = html2[:ao+1], html2[ac:], html2[ao+1:ac]
splits = list(re.finditer(r'(?=\{id:")', body))
entries = []
for i, m in enumerate(splits):
    s = m.start(); e = splits[i+1].start() if i+1 < len(splits) else len(body)
    raw = body[s:e].rstrip(',\n '); cm = re.match(r'\{id:"([^"]+)"', raw)
    entries.append((cm.group(1) if cm else f'UNK_{i}', raw))
top_set = set(TOP_ORDER); code_map = {c: e for c, e in entries}
new_entries = [(c, code_map[c]) for c in TOP_ORDER if c in code_map] + [(c, e) for c, e in entries if c not in top_set]
open(V6_20, 'w', encoding='utf-8').write(before + '\n' + ',\n'.join(e for _, e in new_entries) + '\n' + after)
print(f'  Top 5: {[c for c, _ in new_entries[:5]]}  Total: {len(new_entries)}')

# ── 검증 ─────────────────────────────────────────────────────────────
v_final = open(V6_20, encoding='utf-8').read()
idx2 = v_final.find(f'{{id:"{CODE}"'); nxt2 = v_final.find('{id:"', idx2+10)
e = v_final[idx2:nxt2]
print(f'\n✅ {CODE} gal:{e[:e.find("feat:")].count("{a:\"View ")} feat:{e[e.find("feat:"):e.find(",sp:")].count("{a:\"")} size:{len(e):,}')
