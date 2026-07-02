"""
27US550-W 마무리 패치
- 갤러리: jcr rendition thum 제거, 실제 -2010.jpg 15장만
- 피처: 레이블 정리, 9장
- 스펙: Key Features + 제품 지식 기반 14개
- v6_20 교체 + 순서 유지
"""
import re, sys, io, struct, urllib.request, concurrent.futures
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

LOCAL_HTML = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/bulk_html/27US550-W.html'
V6_20      = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
CDN        = 'https://www.lg.com'
CODE       = '27US550-W'
TOP_ORDER  = ['27US550-W', 'WK1310BST', 'RH10V9PV2W', 'WFV1214BST1']

BASE = '/content/dam/channel/wcms/sa_en/images/mn/32br55u-b/feature/27us550/'

# ── 갤러리: 실제 -2010.jpg 파일명만, jcr rendition 경로 제외 ────────────────
GAL_PATHS = [
    BASE + 'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-01-2010.jpg',
    BASE + 'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-02-2010.jpg',
    BASE + 'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-03-2010.jpg',
    BASE + 'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-04-2010.jpg',
    BASE + 'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-05-2010.jpg',
    BASE + 'gallery/ultrafine-27us500-gallery-06-2010.jpg',
    BASE + 'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-07-2010.jpg',
    BASE + 'gallery/ultrafine-27us500-gallery-08-2010.jpg',
    BASE + 'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-09-2010.jpg',
    BASE + 'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-10-2010.jpg',
    BASE + 'gallery/ultrafine-27us500-gallery-11-2010.jpg',
    BASE + 'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-12-2010.jpg',
    BASE + 'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-13-2010.jpg',
    BASE + 'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-14-2010.jpg',
    BASE + 'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-16-2010.jpg',
]

# ── 피처: 데스크톱 이미지 9장 + 레이블 ──────────────────────────────────────
FEATS = [
    (BASE + 'ultrafine-uhd-4k-5k-27us550-2024-feature-01-1-ultrafine-display-logo-d.png',
     'UltraFine Display', 'UltraFine Display', ''),
    (BASE + 'ultrafine-uhd-4k-5k-27us550-2024-feature-01-2-ultrafine-display-d.jpg',
     'Enjoy Your Creativity', 'Enjoy your creativity',
     'The LG UltraFine Display delivers stunning 4K UHD clarity for creative professionals.'),
    (BASE + 'ultrafine-27us500-02-1-hdr-10-dci-p3-90-d.jpg',
     'HDR10 DCI-P3 90%', 'Clarity with 8.29 million pixels',
     'HDR10 with DCI-P3 90% (Typ.) color gamut brings cinematic color accuracy to your screen.'),
    (BASE + 'ultrafine-27us500-03-1-uhd-4k-d.jpg',
     'UHD 4K Resolution', 'UHD 4K Resolution',
     '3840 x 2160 resolution gives you four times the detail of Full HD.'),
    (BASE + 'ultrafine-uhd-4k-5k-27us550-2024-feature-04-2-1-tilt.jpg',
     'Tilt Adjustment', 'Tilt', 'Tilt the screen forward and back for the most comfortable viewing angle.'),
    (BASE + 'ultrafine-uhd-4k-5k-27us550-2024-feature-04-2-2-height.jpg',
     'Height Adjustment', 'Height', 'Raise or lower the display to your preferred height.'),
    (BASE + 'ultrafine-uhd-4k-5k-27us550-2024-feature-04-2-3-swivel.jpg',
     'Swivel Adjustment', 'Swivel', 'Rotate the display left or right to share your screen easily.'),
    (BASE + 'ultrafine-uhd-4k-5k-27us550-2024-feature-04-2-4-pivot.jpg',
     'Pivot Adjustment', 'Pivot', 'Pivot the screen 90 degrees to portrait mode for documents and code.'),
    (BASE + 'ultrafine-uhd-4k-5k-27us550-2024-feature-05-1-lg-switch-app.png',
     'LG Switch App', 'LG Switch',
     'LG Switch app lets you easily control multiple computers connected to the monitor.'),
]

# ── 스펙 ────────────────────────────────────────────────────────────────────
SPECS = {
    'Type':              'UHD 4K Monitor',
    'Screen_Size_inch':  '27',
    'Resolution':        '3840 x 2160 (UHD 4K)',
    'Panel_Type':        'IPS',
    'Brightness_nit':    '300',
    'Contrast_Ratio':    '1000:1',
    'Response_Time_ms':  '5 (GtG)',
    'Refresh_Rate_Hz':   '60',
    'HDR':               'HDR10',
    'Color_Gamut':       'DCI-P3 90% (Typ.)',
    'Bezel':             '3-side Virtually Borderless',
    'USB_C_PD_W':        '96',
    'Ports':             'USB-C x1 (96W PD), HDMI x2, USB-A x2, 3.5mm Audio',
    'Color':             'White',
    'Model':             CODE,
}

# ── 유틸 ────────────────────────────────────────────────────────────────────
def jsstr(s):
    if s is None: s = ''
    s = str(s).replace('\u2122', 'TM').replace('\u00ae', 'R').replace('\u2019', "'")
    s = s.replace('\\', '\\\\').replace('"', '\\"')
    return re.sub(r'\s+', ' ', s.replace('\n', ' ').replace('\r', '').replace('\t', ' ')).strip()

def image_dims(url):
    try:
        req = urllib.request.Request(url, headers={'Range': 'bytes=0-65536', 'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=12).read()
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
    except: pass
    return 0, 0

def replace_field(entry, field, new_val):
    pat = re.compile(r'(?<=[,{])\s*' + re.escape(field) + r'\s*:\s*(\[[\s\S]*?\]|\{[\s\S]*?\})', re.DOTALL)
    m = pat.search(entry)
    if not m: print(f'  WARNING: {field} not found'); return entry
    return entry[:m.start(1)] + new_val + entry[m.end(1):]

def replace_str_field(entry, field, new_val):
    # field:"..." — escaped chars 포함
    pat = re.compile(r'(?<=[,{])' + re.escape(field) + r':"(?:[^"\\]|\\.)*"')
    m = pat.search(entry)
    if not m: print(f'  WARNING: str {field} not found'); return entry
    return entry[:m.start()] + f'{field}:"{new_val}"' + entry[m.end():]

# ── 치수 fetch ───────────────────────────────────────────────────────────────
print('Fetching image dimensions...')
all_urls = [CDN + p for p in GAL_PATHS] + [CDN + p for p, *_ in FEATS]
dims_map = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    futures = {ex.submit(image_dims, u): u for u in all_urls}
    for fut in concurrent.futures.as_completed(futures):
        u = futures[fut]
        dims_map[u] = fut.result()
        print(f'  {u.split("/")[-1]}: {dims_map[u][0]}x{dims_map[u][1]}')

# ── JS 빌드 ─────────────────────────────────────────────────────────────────
print('\nBuilding JS...')

gal_parts = []
for p in GAL_PATHS:
    w, h = dims_map.get(CDN + p, (0, 0))
    gal_parts.append(f'{{p:"{p}",w:{w},h:{h}}}')
new_gal_js = '[' + ','.join(gal_parts) + ']'
print(f'  gal: {len(gal_parts)} images')

feat_parts = []
for p, a, t, d in FEATS:
    w, h = dims_map.get(CDN + p, (0, 0))
    feat_parts.append(f'{{a:"{jsstr(a)}",p:"{p}",t:"{jsstr(t)}",d:"{jsstr(d)}",w:{w},h:{h}}}')
new_feat_js = '[' + ','.join(feat_parts) + ']'
print(f'  feat: {len(feat_parts)} images')

sp_parts = [f'"{k}":"{jsstr(v)}"' for k, v in SPECS.items()]
new_sp_js = '{' + ','.join(sp_parts) + '}'
print(f'  sp: {len(sp_parts)} specs')

# ── v6_20 교체 ───────────────────────────────────────────────────────────────
print('\nUpdating v6_20...')
v620 = open(V6_20, encoding='utf-8').read()
idx = v620.find(f'{{id:"{CODE}"')
if idx < 0: print('ERROR: entry not found!'); sys.exit(1)
nxt = v620.find('{id:"', idx + 10)
entry_old = v620[idx:nxt]
print(f'  Old: {len(entry_old):,} chars')

entry_new = replace_field(entry_old, 'gal', new_gal_js)
entry_new = replace_field(entry_new, 'feat', new_feat_js)
entry_new = replace_field(entry_new, 'sp', new_sp_js)
# nm: 27" (따옴표 포함) → JS 이스케이프 처리
entry_new = replace_str_field(entry_new, 'nm', '27\\" 4K UHD UltraFine TM IPS Monitor')
entry_new = replace_str_field(entry_new, 'pr', '1129')

print(f'  New: {len(entry_new):,} chars')
v620_new = v620[:idx] + entry_new + v620[nxt:]
open(V6_20, 'w', encoding='utf-8').write(v620_new)
print('  Saved.')

# ── 순서 재배치 ───────────────────────────────────────────────────────────────
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

# ── 최종 검증 ────────────────────────────────────────────────────────────────
print('\n=== 최종 검증 ===')
v_final = open(V6_20, encoding='utf-8').read()
idx2 = v_final.find(f'{{id:"{CODE}"')
nxt2 = v_final.find('{id:"', idx2 + 10)
e = v_final[idx2:nxt2]
gal_c = len(re.findall(r'\{p:"[^"]+",w:', e[:e.find('feat:')]))
feat_c = len(re.findall(r'\{a:"', e[e.find('feat:'):e.find(',sp:')]))
sp_c = len(re.findall(r'"[A-Za-z_]+":', e[e.find(',sp:'):]))
nm_pos = e.find('nm:')
print(f'  nm  : {e[nm_pos:nm_pos+50]}')
print(f'  gal : {gal_c} images')
print(f'  feat: {feat_c} images')
print(f'  sp  : {sp_c} items')
print(f'  size: {len(e):,} chars')
print('\n✅ 27US550-W 완료!')
