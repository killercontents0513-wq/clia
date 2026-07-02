"""27US550-W 통합 스크립트: 기존 잘못된 WashTower 데이터를 올바른 모니터 데이터로 교체"""
import re, sys, io, struct, urllib.request, concurrent.futures
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

LOCAL_HTML = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/bulk_html/27US550-W.html'
V6_20      = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
CDN        = 'https://www.lg.com'
BASE_PATH  = '/content/dam/channel/wcms/sa_en/images/mn/32br55u-b/feature/27us550/'

# ── 이미지 목록 (갤러리 15장, 피처 9장) ────────────────────────────────────
GAL_FILES = [
    'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-01-2010.jpg',
    'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-02-2010.jpg',
    'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-03-2010.jpg',
    'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-04-2010.jpg',
    'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-05-2010.jpg',
    'gallery/ultrafine-27us500-gallery-06-2010.jpg',
    'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-07-2010.jpg',
    'gallery/ultrafine-27us500-gallery-08-2010.jpg',
    'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-09-2010.jpg',
    'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-10-2010.jpg',
    'gallery/ultrafine-27us500-gallery-11-2010.jpg',
    'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-12-2010.jpg',
    'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-13-2010.jpg',
    'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-14-2010.jpg',
    'gallery/ultrafine-uhd-4k-5k-27us550-2024-gallery-16-2010.jpg',
]

FEAT_FILES = [
    'ultrafine-uhd-4k-5k-27us550-2024-feature-01-1-ultrafine-display-logo-d.png',
    'ultrafine-uhd-4k-5k-27us550-2024-feature-01-2-ultrafine-display-d.jpg',
    'ultrafine-27us500-02-1-hdr-10-dci-p3-90-d.jpg',
    'ultrafine-27us500-03-1-uhd-4k-d.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-feature-04-2-1-tilt.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-feature-04-2-2-height.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-feature-04-2-3-swivel.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-feature-04-2-4-pivot.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-feature-05-1-lg-switch-app.png',
]

FEAT_LABELS = [
    'UltraFine Display Logo',
    'UltraFine Display',
    'HDR10 DCI-P3 90%',
    'UHD 4K Resolution',
    'Tilt Adjustment',
    'Height Adjustment',
    'Swivel Adjustment',
    'Pivot Adjustment',
    'LG Switch App',
]

# ── 스펙 (제품 지식 기반 + HTML 추출 보강) ──────────────────────────────────
SPECS_BASE = {
    'Type':               'UHD 4K Monitor',
    'Screen_Size_inch':   '27',
    'Resolution':         '3840 x 2160 (UHD 4K)',
    'Panel_Type':         'IPS',
    'Brightness_nit':     '250',
    'Contrast_Ratio':     '1000:1',
    'Response_Time_ms':   '5 (GtG)',
    'Refresh_Rate_Hz':    '60',
    'HDR':                'HDR10',
    'Color_Gamut':        'DCI-P3 90%',
    'Ports':              'USB-C (96W PD), 2x HDMI, 2x USB-A, 3.5mm Audio',
    'USB_C_Power_W':      '96',
    'Connectivity':       'USB-C, HDMI',
    'Color':              'White',
    'Model':              '27US550-W',
}

# ── 유틸 ────────────────────────────────────────────────────────────────────
def jsstr(s):
    if s is None: s = ''
    s = str(s).replace('\u2122', 'TM').replace('\u00ae', 'R')
    s = s.replace('\\', '\\\\').replace('"', '\\"')
    return re.sub(r'\s+', ' ', s.replace('\n', ' ').replace('\r', '').replace('\t', ' ')).strip()

def image_dims(url):
    try:
        req = urllib.request.Request(url, headers={
            'Range': 'bytes=0-65536',
            'User-Agent': 'Mozilla/5.0'
        })
        data = urllib.request.urlopen(req, timeout=10).read()
        # JPEG
        if data[:2] == b'\xff\xd8':
            i = 2
            while i < len(data) - 9:
                if data[i] != 0xff: break
                marker = data[i+1]
                length = struct.unpack('>H', data[i+2:i+4])[0]
                if marker in (0xC0, 0xC2):
                    h = struct.unpack('>H', data[i+5:i+7])[0]
                    w = struct.unpack('>H', data[i+7:i+9])[0]
                    return w, h
                i += 2 + length
        # PNG
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            w = struct.unpack('>I', data[16:20])[0]
            h = struct.unpack('>I', data[20:24])[0]
            return w, h
        # WEBP
        if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            if data[12:16] == b'VP8 ':
                w = struct.unpack('<H', data[26:28])[0] & 0x3FFF
                h = struct.unpack('<H', data[28:30])[0] & 0x3FFF
                return w, h
            elif data[12:16] == b'VP8L':
                bits = struct.unpack('<I', data[21:25])[0]
                w = (bits & 0x3FFF) + 1
                h = ((bits >> 14) & 0x3FFF) + 1
                return w, h
            elif data[12:16] == b'VP8X':
                w = (struct.unpack('<I', data[24:27] + b'\x00')[0]) + 1
                h = (struct.unpack('<I', data[27:30] + b'\x00')[0]) + 1
                return w, h
    except Exception as e:
        print(f'  dim error {url[-50:]}: {e}')
    return 0, 0

def get_feat_text(html, filename):
    """파일명 stem으로 HTML에서 위치를 찾아 headline/body 추출"""
    stem = filename.rsplit('.', 1)[0]
    positions = [m.start() for m in re.finditer(re.escape(stem), html)]
    # 피처 섹션 범위(100k~900k) 내 위치 선택
    best = next((p for p in positions if 100000 < p < 1800000), None)
    if best is None and positions:
        best = positions[0]
    if best is None:
        return '', ''
    snip = html[best:best + 4000]
    hl_m = re.search(r'c-text-contents__headline[^>]*>([\s\S]{1,400}?)</div', snip)
    bd_m = re.search(r'c-text-contents__body[^>]*>([\s\S]{1,800}?)</div', snip)
    def clean(m):
        if not m: return ''
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    return clean(hl_m), clean(bd_m)

def replace_field(entry, field, new_val):
    pat = re.compile(
        r'(?<=[,{])\s*' + re.escape(field) + r'\s*:\s*(\[[\s\S]*?\]|\{[\s\S]*?\})',
        re.DOTALL)
    m = pat.search(entry)
    if not m:
        print(f'  WARNING: {field} not found')
        return entry
    return entry[:m.start(1)] + new_val + entry[m.end(1):]

def replace_str_field(entry, field, new_val):
    pat = re.compile(
        r'(?<=[,{])\s*' + re.escape(field) + r'\s*:\s*"([^"]*)"')
    m = pat.search(entry)
    if not m:
        print(f'  WARNING: str field {field} not found')
        return entry
    return entry[:m.start(1)] + new_val + entry[m.end(1):]

# ── HTML 로드 ────────────────────────────────────────────────────────────────
print('Loading local HTML...')
html = open(LOCAL_HTML, encoding='utf-8').read()
print(f'  HTML: {len(html):,} chars')

# ── 가격 추출 ────────────────────────────────────────────────────────────────
price_m = re.search(r'"price"\s*:\s*"?([\d,\.]+)"?', html)
price = price_m.group(1).replace(',', '') if price_m else '1129'
print(f'  Price: SAR {price}')

# ── 제품명 추출 ───────────────────────────────────────────────────────────────
nm_m = re.search(r'"name"\s*:\s*"([^"]+)"', html)
nm = nm_m.group(1) if nm_m else '27" 4K UHD UltraFine IPS Monitor'
print(f'  Name: {nm}')

# ── HTML 스펙 추출 ────────────────────────────────────────────────────────────
specs = dict(SPECS_BASE)
spec_pairs = re.findall(
    r'c-compare-selling__spec-name[^>]*>([\s\S]{1,200}?)</(?:p|div|span)>[\s\S]{0,300}?c-compare-selling__spec-desc[^>]*>([\s\S]{1,400}?)</(?:p|div|span)>',
    html)
print(f'  HTML specs found: {len(spec_pairs)}')
for sn, sd in spec_pairs:
    k = re.sub(r'\s+', '_', re.sub(r'[^A-Za-z0-9 _]', '', re.sub(r'<[^>]+>', '', sn).strip()))
    v = re.sub(r'<[^>]+>', '', sd).strip()
    v = re.sub(r'\s+', ' ', v)
    if k and v:
        specs[k] = v
        print(f'    {k}: {v[:60]}')

# ── 이미지 치수 병렬 fetch ───────────────────────────────────────────────────
gal_urls  = [CDN + BASE_PATH + f for f in GAL_FILES]
feat_urls = [CDN + BASE_PATH + f for f in FEAT_FILES]
all_urls  = gal_urls + feat_urls

print(f'\nFetching dimensions for {len(all_urls)} images...')
dims_map = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    futures = {ex.submit(image_dims, u): u for u in all_urls}
    for fut in concurrent.futures.as_completed(futures):
        u = futures[fut]
        dims_map[u] = fut.result()
        w, h = dims_map[u]
        fn = u.split('/')[-1]
        print(f'  {fn}: {w}x{h}')

# ── 갤러리 JS 빌드 ────────────────────────────────────────────────────────────
gal_parts = []
for i, fn in enumerate(GAL_FILES):
    url = CDN + BASE_PATH + fn
    w, h = dims_map.get(url, (0, 0))
    gal_parts.append(f'{{p:"{BASE_PATH + fn}",w:{w},h:{h}}}')
new_gal_js = '[' + ','.join(gal_parts) + ']'
print(f'\nGallery: {len(gal_parts)} images')

# ── 피처 JS 빌드 ─────────────────────────────────────────────────────────────
feat_parts = []
for i, fn in enumerate(FEAT_FILES):
    url = CDN + BASE_PATH + fn
    w, h = dims_map.get(url, (0, 0))
    label = FEAT_LABELS[i] if i < len(FEAT_LABELS) else f'Feature {i+1}'
    t, d = get_feat_text(html, fn)
    if not t:
        t = label
    feat_parts.append(
        f'{{a:"{jsstr(label)}",p:"{BASE_PATH + fn}",t:"{jsstr(t)}",d:"{jsstr(d)}",w:{w},h:{h}}}')
    print(f'  [{i+1}] {fn[-40:]}: {jsstr(t)[:50]}')
new_feat_js = '[' + ','.join(feat_parts) + ']'
print(f'Features: {len(feat_parts)} images')

# ── 스펙 JS 빌드 ─────────────────────────────────────────────────────────────
sp_parts = [f'"{k}":"{jsstr(v)}"' for k, v in specs.items()]
new_sp_js = '{' + ','.join(sp_parts) + '}'
print(f'Specs: {len(specs)} items')

# ── v6_20 엔트리 교체 ────────────────────────────────────────────────────────
print('\nUpdating v6_20...')
v620 = open(V6_20, encoding='utf-8').read()
idx = v620.find('{id:"27US550-W"')
if idx < 0:
    print('ERROR: 27US550-W entry not found!')
    sys.exit(1)
nxt = v620.find('{id:"', idx + 10)
entry = v620[idx:nxt]
print(f'  Entry found: {len(entry):,} chars')

entry_new = replace_field(entry, 'gal', new_gal_js)
entry_new = replace_field(entry_new, 'feat', new_feat_js)
entry_new = replace_field(entry_new, 'sp', new_sp_js)
entry_new = replace_str_field(entry_new, 'nm', jsstr(nm))
entry_new = replace_str_field(entry_new, 'pr', price)

print(f'  Entry: {len(entry):,} -> {len(entry_new):,} chars')

v620_new = v620[:idx] + entry_new + v620[nxt:]
open(V6_20, 'w', encoding='utf-8').write(v620_new)
print('  v6_20 saved.')

# ── 순서 재배치: 27US550-W → WK1310BST → RH10V9PV2W → WFV1214BST1 ──────────
TOP_ORDER = ['27US550-W', 'WK1310BST', 'RH10V9PV2W', 'WFV1214BST1']

html2 = open(V6_20, encoding='utf-8').read()
first_id  = html2.find('{id:"')
arr_open  = html2.rfind('[', 0, first_id)
arr_close = html2.find('];', first_id)
before    = html2[:arr_open + 1]
after     = html2[arr_close:]
arr_body  = html2[arr_open + 1:arr_close]

splits = list(re.finditer(r'(?=\{id:")', arr_body))
entries = []
for i, m in enumerate(splits):
    start = m.start()
    end   = splits[i+1].start() if i+1 < len(splits) else len(arr_body)
    raw   = arr_body[start:end].rstrip(',\n ')
    code_m = re.match(r'\{id:"([^"]+)"', raw)
    code  = code_m.group(1) if code_m else f'UNKNOWN_{i}'
    entries.append((code, raw))

print(f'\nTotal entries: {len(entries)}')
print('Before:', [c for c, _ in entries[:5]])

top_codes = set(TOP_ORDER)
code_map  = {c: e for c, e in entries}
top_entries  = [(c, code_map[c]) for c in TOP_ORDER if c in code_map]
rest_entries = [(c, e) for c, e in entries if c not in top_codes]

new_entries = top_entries + rest_entries
new_body = ',\n'.join(e for _, e in new_entries)
new_html = before + '\n' + new_body + '\n' + after

with open(V6_20, 'w', encoding='utf-8') as f:
    f.write(new_html)

print('After :', [c for c, _ in new_entries[:5]])
print(f'\n✅ 27US550-W integrated & reordered!')
print(f'   Top 4: {[c for c,_ in new_entries[:4]]}')
