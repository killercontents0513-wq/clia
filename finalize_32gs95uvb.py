"""
32GS95UV-B 마무리 패치
- 갤러리: basic-large 제거, View N 라벨 + w/h 추가 (15장)
- 피처: 핵심 12장 선별 (desktop -d.jpg), 라벨/타이틀/설명 추가
- 스펙: 핵심 스펙 재정리 (raw spec key 교체)
- 제품명/가격 수정
- 1번 순서로 재배치
- 치수: 순차 fetch (Rate-limit 회피)
"""
import re, sys, io, struct, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

V6_20    = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
CODE     = '32GS95UV-B'
CDN_BASE = 'https://www.lg.com/content/dam/channel/wcms/sa_en'

TOP_ORDER = ['32GS95UV-B', 'WTV17HHD', '27US550-W', 'WK1310BST', 'RH10V9PV2W', 'WFV1214BST1']

# ── 갤러리 (15장, -2010.jpg) ───────────────────────────────────────────
GAL_PATHS = [
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-01-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-02-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-03-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-04-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-05-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-06-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-07-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-08-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-09-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-10-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-11-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-12-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-13-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-14-2010.jpg',
    '/images/monitors/32gs95uv-b/ultragear-32gs95uv-b-gallery-15-2010.jpg',
]

# ── 핵심 피처 12장 (desktop -d.jpg, 핵심 기능 선별) ──────────────────────
BASE_F = '/images/monitors/gs95uv-b/'
FEAT_LIST = [
    (BASE_F + 'ultragear-32gs95uv-b-01-4-lg-ultragear-oled-d.jpg',
     'LG UltraGear OLED', 'World\'s First 32" 4K OLED Gaming Monitor',
     'The LG UltraGear OLED delivers the world\'s first 32" 4K OLED gaming experience.'),
    (BASE_F + 'ultragear-32gs95uv-b-02-1-32-inch-4k-oled-d.jpg',
     '32" 4K OLED', '32" 4K UHD OLED Panel',
     '3840x2160 resolution on a stunning OLED panel with perfect blacks and vivid colors.'),
    (BASE_F + 'ultragear-32gs95uv-b-03-1-dual-mode-d.jpg',
     'Dual-Mode', '4K@240Hz or FHD@480Hz',
     'Switch between 4K@240Hz for cinematic clarity or FHD@480Hz for ultra-competitive gaming.'),
    (BASE_F + 'ultragear-32gs95uv-b-04-1-bright-oled-d.jpg',
     'Bright OLED', '1,300 Nits Peak Brightness',
     'Bright OLED technology delivers 1,300 nits peak brightness for vivid HDR performance.'),
    (BASE_F + 'ultragear-32gs95uv-b-05-1-micro-lens-array.jpg',
     'Micro Lens Array', 'Micro Lens Array Technology',
     'Micro Lens Array enhances brightness while maintaining the deep blacks OLED is known for.'),
    (BASE_F + 'ultragear-32gs95uv-b-06-1-hdr-true-black-400-dci-p3-98.5.jpg',
     'HDR True Black 400', 'DisplayHDR True Black 400 — DCI-P3 98.5%',
     'Certified DisplayHDR True Black 400 with DCI-P3 98.5% for true cinematic color accuracy.'),
    (BASE_F + 'ultragear-32gs95uv-b-07-1-0.03ms-gtg-response-time.jpg',
     '0.03ms Response', '0.03ms (GtG) Response Time',
     'Blazing 0.03ms GtG response eliminates ghosting and motion blur for the clearest action.'),
    (BASE_F + 'ultragear-32gs95uv-b-10-1-flud-smooth-gaming-visual-d.jpg',
     'Smooth Gaming', 'FreeSync Premium Pro & G-SYNC Compatible',
     'AMD FreeSync Premium Pro and NVIDIA G-SYNC Compatible ensure tear-free smooth gameplay.'),
    (BASE_F + 'ultragear-32gs95uv-b-11-2-vesa-clearmr-13000-d.jpg',
     'VESA ClearMR 13000', 'VESA ClearMR 13000 Certified',
     'VESA ClearMR 13000 certification guarantees exceptional motion clarity for gaming.'),
    (BASE_F + 'ultragear-32gs95uv-b-14-1-dp-1.4-hdmi-2.1-240hz-d.jpg',
     'DP 1.4 & HDMI 2.1', 'DisplayPort 1.4 + HDMI 2.1 at 240Hz',
     'Full-bandwidth DP 1.4 and HDMI 2.1 support 4K@240Hz without compression.'),
    (BASE_F + 'ultragear-32gs95uv-b-09-2-1-unity-hexagonal-design-d.jpg',
     'Sphere Lighting 2.0', 'Unity Hexagonal Design',
     'Sphere Lighting 2.0 with Unity Hexagonal Design creates an immersive gaming ambiance.'),
    (BASE_F + 'ultragear-32gs95uv-b-08-1-7w-speaker-d.jpg',
     '7W x2 Speakers', 'Built-in DTS Virtual:X Speakers',
     'Dual 7W speakers with DTS Virtual:X deliver powerful spatial audio for gaming immersion.'),
]

# ── 핵심 스펙 ──────────────────────────────────────────────────────────
SPECS = {
    'Type':                    'Gaming Monitor',
    'Screen_Size_inch':        '31.5 (32")',
    'Resolution':              '3840 x 2160 (4K UHD)',
    'Panel_Type':              'OLED (Micro Lens Array)',
    'Dual_Mode':               '4K@240Hz / FHD@480Hz',
    'Refresh_Rate_Hz':         '240 (4K) / 480 (FHD)',
    'Response_Time_ms':        '0.03 (GtG)',
    'Brightness_nit':          '275 (Typ.) / 1300 (Peak)',
    'Contrast_Ratio':          '1,500,000:1',
    'HDR':                     'DisplayHDR True Black 400',
    'Color_Gamut':             'DCI-P3 98.5% (Typ.)',
    'Sync':                    'NVIDIA G-SYNC Compatible, AMD FreeSync Premium Pro',
    'VESA_ClearMR':            '13000',
    'Ports':                   'DP 1.4 x1, HDMI 2.1 x2, USB-A x2, Headphone 4-pole',
    'Speakers':                '7W x2, DTS Virtual:X',
    'Ergonomics':              'Tilt / Height / Swivel / Pivot',
    'Color':                   'Matte Black',
    'Dimensions_WxHxD_mm':    '714.1 x 620.9 x 249.8 (Stand Up)',
    'Weight_with_Stand_kg':    '9.8',
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
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
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
print('Fetching dimensions (sequential)...')
all_paths = GAL_PATHS + [p for p, *_ in FEAT_LIST]
dims = {}
for p in all_paths:
    url = CDN_BASE + p
    w, h = image_dims(url)
    dims[p] = (w, h)
    fn = p.split('/')[-1]
    print(f'  {fn}: {w}x{h}')
    time.sleep(0.1)

# ── JS 빌드 ───────────────────────────────────────────────────────────
print('\nBuilding JS...')

# 갤러리
gal_parts = []
for i, p in enumerate(GAL_PATHS, 1):
    w, h = dims.get(p, (0, 0))
    gal_parts.append(f'{{a:"View {i}",p:"{p}",w:{w},h:{h}}}')
new_gal_js = '[' + ','.join(gal_parts) + ']'
print(f'  gal: {len(gal_parts)} images')

# 피처
feat_parts = []
for p, a, t, d in FEAT_LIST:
    w, h = dims.get(p, (0, 0))
    feat_parts.append(f'{{a:"{jsstr(a)}",p:"{p}",t:"{jsstr(t)}",d:"{jsstr(d)}",w:{w},h:{h}}}')
new_feat_js = '[' + ','.join(feat_parts) + ']'
print(f'  feat: {len(feat_parts)} images')

# 스펙
sp_parts = [f'"{k}":"{jsstr(v)}"' for k, v in SPECS.items()]
new_sp_js = '{' + ','.join(sp_parts) + '}'
print(f'  sp: {len(sp_parts)} specs')

# ── v6_20 교체 ────────────────────────────────────────────────────────
print('\nUpdating v6_20...')
v620 = open(V6_20, encoding='utf-8').read()
idx = v620.find(f'{{id:"{CODE}"')
if idx < 0: print('ERROR: entry not found!'); sys.exit(1)
nxt = v620.find('{id:"', idx + 10)
entry_old = v620[idx:nxt]
print(f'  Old: {len(entry_old):,} chars')

CORRECT_NM = '32\\" UltraGear OLED Dual-Mode Gaming Monitor'
entry_new = replace_field(entry_old, 'gal', new_gal_js)
entry_new = replace_field(entry_new, 'feat', new_feat_js)
entry_new = replace_field(entry_new, 'sp', new_sp_js)
entry_new = replace_str_field(entry_new, 'nm', CORRECT_NM)
entry_new = replace_str_field(entry_new, 'pr', '5499')

print(f'  New: {len(entry_new):,} chars')
v620_new = v620[:idx] + entry_new + v620[nxt:]
open(V6_20, 'w', encoding='utf-8').write(v620_new)
print('  Saved.')

# ── 순서 재배치 ────────────────────────────────────────────────────────
print('\nReordering...')
html2 = open(V6_20, encoding='utf-8').read()
fi = html2.find('{id:"')
ao = html2.rfind('[', 0, fi)
ac = html2.find('];', fi)
before, after, body = html2[:ao+1], html2[ac:], html2[ao+1:ac]

splits = list(re.finditer(r'(?=\{id:")', body))
entries = []
for i, m in enumerate(splits):
    s = m.start()
    e = splits[i+1].start() if i+1 < len(splits) else len(body)
    raw = body[s:e].rstrip(',\n ')
    cm = re.match(r'\{id:"([^"]+)"', raw)
    entries.append((cm.group(1) if cm else f'UNK_{i}', raw))

top_set = set(TOP_ORDER)
code_map = {c: e for c, e in entries}
new_entries = [(c, code_map[c]) for c in TOP_ORDER if c in code_map] + \
              [(c, e) for c, e in entries if c not in top_set]
open(V6_20, 'w', encoding='utf-8').write(before + '\n' + ',\n'.join(e for _, e in new_entries) + '\n' + after)
print(f'  Top 5: {[c for c, _ in new_entries[:5]]}')
print(f'  Total: {len(new_entries)}')

# ── 최종 검증 ─────────────────────────────────────────────────────────
print('\n=== 최종 확인 ===')
v_final = open(V6_20, encoding='utf-8').read()
idx2 = v_final.find(f'{{id:"{CODE}"')
nxt2 = v_final.find('{id:"', idx2 + 10)
e = v_final[idx2:nxt2]
nm_m = re.search(r'nm:"((?:[^"\\]|\\.)*)"', e)
pr_m = re.search(r',pr:"([^"]*)"', e)
gal_c = len(re.findall(r'\{a:"View ', e[:e.find('feat:')]))
feat_c = len(re.findall(r'\{a:"', e[e.find('feat:'):e.find(',sp:')]))
sp_c = len(re.findall(r'"[A-Za-z_]+":', e[e.find(',sp:'):]))
print(f'  nm  : {nm_m.group(1) if nm_m else "?"}')
print(f'  pr  : {pr_m.group(1) if pr_m else "?"}')
print(f'  gal : {gal_c}장')
print(f'  feat: {feat_c}장')
print(f'  sp  : {sp_c}개')
print(f'  size: {len(e):,} chars')
print(f'\n✅ {CODE} 완료!')
