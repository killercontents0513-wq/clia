"""
LT19HBHSIN 재크롤 (v2)
- 갤러리: hr-images/DZ-01~12 (12장, 데스크탑 제품 사진)
- 피처: 실제 LG.com Key Features 4개 (페이지 keyFeatureList 기반) + DZ 이미지 매핑
- 스펙: LG.com 페이지 c-compare-selling 에서 실제 추출된 17개 핵심 스펙
"""
import re, sys, io, struct, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

V6_20    = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
CODE     = 'LT19HBHSIN'
CDN_BASE = 'https://www.lg.com/content/dam/channel/wcms/sa_en'

TOP_ORDER = ['LSEL6333D', 'LT19HBHSIN', 'S90TR', 'S80TR', 'S45TR', '32GS95UV-B', 'WTV17HHD', '27US550-W', 'WK1310BST', 'RH10V9PV2W', 'WFV1214BST1']

# ── 갤러리: 진짜 제품 사진 large01~15 (LG canonical /gallery/ 폴더) ────
GAL_BASE = '/images/refrigerators/lt19hbhsin/gallery/'
GAL_PATHS = [GAL_BASE + f'large{str(i).zfill(2)}.jpg' for i in range(1, 16)]

# 피처 이미지는 hr-images 의 DZ 시리즈 사용 (illustrative)
BASE = '/images/refrigerators/lt19hbhsin-apzgngh/hr-images/'

# ── 피처: 실제 LG.com Key Features (4개) + DZ 이미지 매핑 ──────────────
# Source: id="keyFeatureList" on https://www.lg.com/sa_en/refrigerators/top-freezers/lt19hbhsin/
# Note: 이 페이지는 dedicated /features/ 이미지가 없음 → DZ 갤러리 이미지를 illustrative 로 매핑
FEAT_LIST = [
    (BASE + 'DZ-04.jpg',
     'Smart Inverter', 'Smart Inverter Compressor',
     'Smart Inverter Compressor (BLDC) delivers energy efficiency and durability with a 10-year warranty.'),
    (BASE + 'DZ-06.jpg',
     'LINEARCooling', 'LINEARCooling — Minimum Temperature Fluctuations',
     'LINEARCooling minimizes temperature fluctuations within ±0.5°C to keep food fresher for longer.'),
    (BASE + 'DZ-08.jpg',
     'Hygiene FRESH+', 'Hygiene FRESH+ — 5-Step Filtering',
     'Hygiene FRESH+ uses 5-step filtering to purify internal air, reducing bacteria and odors.'),
    (BASE + 'DZ-10.jpg',
     'ThinQ', 'ThinQ Smart Diagnose & Wi-Fi Control',
     'Control and monitor your refrigerator remotely with the LG ThinQ app, including Smart Diagnose.'),
]

# ── 스펙: LG.com 실제 추출 (c-compare-selling) → 18 핵심 필드 ──────────
SPECS = {
    'Type':                    'Top Freezer Refrigerator',
    'Product_Type':            'Top Mount',
    'Total_Capacity_L':        '506',
    'Fridge_Capacity_L':       '376',
    'Freezer_Capacity_L':      '120',
    'Compressor_Type':         'Smart Inverter Compressor (BLDC)',
    'LINEAR_Cooling':          'Yes',
    'Multi_Air_Flow':          'Yes',
    'Door_Cooling_Plus':       'Yes',
    'Fresh_0_Zone':            'Yes',
    'Hygiene_Fresh_Plus':      'No',
    'ThinQ_WiFi':              'Yes',
    'Smart_Diagnosis':         'Yes',
    'Ice_Maker':               'Manual (Movable)',
    'Refrigerator_Light':      'Top LED',
    'Freezer_Light':           'Top LED',
    'Door_Finish':             'P/S3',
    'Dimensions_WxHxD_mm':     '780 x 1800 x 730',
    'Color':                   'Shiny Steel',
    'Model':                   CODE,
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
entry_new = replace_str_field(entry_new, 'nm', 'LG 506L Top Freezer Refrigerator with Smart Inverter')
entry_new = replace_str_field(entry_new, 'pr', '3899')
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
