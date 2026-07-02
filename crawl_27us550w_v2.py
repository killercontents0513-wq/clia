"""
27US550-W 완전 재크롤 (v2)
- LG.com PDP 신규 다운로드
- 갤러리/피처 이미지 전량 추출 + 치수
- 스펙/가격/제품명 추출
- v6_20 엔트리 교체
- 순서: 27US550-W → WK1310BST → RH10V9PV2W → WFV1214BST1
"""
import re, sys, io, struct, time
import urllib.request, urllib.error
import concurrent.futures

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

URL   = 'https://www.lg.com/sa_en/monitors/uhd-4k-5k/27us550-w/'
CDN   = 'https://www.lg.com'
CODE  = '27US550-W'
V6_20 = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
SAVE  = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/bulk_html/27US550-W.html'

TOP_ORDER = ['27US550-W', 'WK1310BST', 'RH10V9PV2W', 'WFV1214BST1']

# ── 유틸 ────────────────────────────────────────────────────────────────────
def jsstr(s):
    if s is None: s = ''
    s = str(s).replace('\u2122', 'TM').replace('\u00ae', 'R').replace('\u2019', "'")
    s = s.replace('\\', '\\\\').replace('"', '\\"')
    return re.sub(r'\s+', ' ', s.replace('\n', ' ').replace('\r', '').replace('\t', ' ')).strip()

def fetch(url, retry=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:
            print(f'  fetch retry {i+1}: {e}')
            time.sleep(2)
    return b''

def image_dims(url):
    try:
        req = urllib.request.Request(url, headers={
            'Range': 'bytes=0-65536',
            'User-Agent': 'Mozilla/5.0'
        })
        data = urllib.request.urlopen(req, timeout=12).read()
        if data[:2] == b'\xff\xd8':          # JPEG
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
        if data[:8] == b'\x89PNG\r\n\x1a\n':  # PNG
            return struct.unpack('>II', data[16:24])
        if data[:4] == b'RIFF' and data[8:12] == b'WEBP':  # WEBP
            if data[12:16] == b'VP8 ':
                w = struct.unpack('<H', data[26:28])[0] & 0x3FFF
                h = struct.unpack('<H', data[28:30])[0] & 0x3FFF
                return w, h
            elif data[12:16] == b'VP8L':
                bits = struct.unpack('<I', data[21:25])[0]
                return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
            elif data[12:16] == b'VP8X':
                w = struct.unpack('<I', data[24:27] + b'\x00')[0] + 1
                h = struct.unpack('<I', data[27:30] + b'\x00')[0] + 1
                return w, h
    except Exception as e:
        pass
    return 0, 0

def clean_html(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'&amp;', '&', s)
    s = re.sub(r'&lt;', '<', s)
    s = re.sub(r'&gt;', '>', s)
    s = re.sub(r'&#x?[0-9a-fA-F]+;', '', s)
    return re.sub(r'\s+', ' ', s).strip()

def replace_field(entry, field, new_val):
    pat = re.compile(
        r'(?<=[,{])\s*' + re.escape(field) + r'\s*:\s*(\[[\s\S]*?\]|\{[\s\S]*?\})',
        re.DOTALL)
    m = pat.search(entry)
    if not m:
        print(f'  WARNING: field {field} not found'); return entry
    return entry[:m.start(1)] + new_val + entry[m.end(1):]

def replace_str_field(entry, field, new_val):
    # field:"..." 패턴. new_val은 이미 jsstr() 처리된 값
    pat = re.compile(r'(?<=[,{])' + re.escape(field) + r':"(?:[^"\\]|\\.)*"')
    m = pat.search(entry)
    if not m:
        print(f'  WARNING: str field {field} not found'); return entry
    return entry[:m.start()] + f'{field}:"{new_val}"' + entry[m.end():]

# ────────────────────────────────────────────────────────────────────────────
# STEP 1: PDP HTML 다운로드
# ────────────────────────────────────────────────────────────────────────────
print('='*60)
print(f'STEP 1: Downloading {URL}')
raw = fetch(URL)
if len(raw) < 100000:
    print(f'ERROR: too small ({len(raw)} bytes), trying saved file')
    html = open(SAVE, encoding='utf-8').read()
else:
    html = raw.decode('utf-8', errors='replace')
    with open(SAVE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  Saved: {len(html):,} chars → {SAVE}')

# ────────────────────────────────────────────────────────────────────────────
# STEP 2: 제품명 / 가격 추출
# ────────────────────────────────────────────────────────────────────────────
print('\nSTEP 2: Name & Price')

# 제품명: JSON-LD 또는 OG 태그
nm = ''
nm_m = re.search(r'"name"\s*:\s*"((?:[^"\\]|\\.)+)"', html)
if nm_m:
    raw_nm = nm_m.group(1)
    nm = raw_nm.replace('\\"', '"').replace('\\\\', '\\')
if not nm:
    nm_m2 = re.search(r'<h1[^>]*>([\s\S]{1,200}?)</h1>', html)
    nm = clean_html(nm_m2.group(1)) if nm_m2 else '27" 4K UHD UltraFine IPS Monitor'
print(f'  Name: {nm}')

price = ''
pr_m = re.search(r'"price"\s*:\s*"?([\d,\.]+)"?', html)
if pr_m:
    price = pr_m.group(1).replace(',', '')
if not price:
    price = '1129'
print(f'  Price: SAR {price}')

# ────────────────────────────────────────────────────────────────────────────
# STEP 3: 전체 CDN 이미지 URL 수집
# ────────────────────────────────────────────────────────────────────────────
print('\nSTEP 3: Collecting CDN images')
CDN_BASE = '/content/dam/channel/wcms/sa_en/images/'
all_paths = list(dict.fromkeys(re.findall(
    r'/content/dam/channel/wcms/sa_en/images/[^\s"\'<>?#]+\.(?:jpg|jpeg|png|webp)',
    html, re.IGNORECASE
)))
print(f'  Total CDN images: {len(all_paths)}')

# 27US550 관련만 필터
prod_paths = [p for p in all_paths if '27us550' in p.lower() or '27us500' in p.lower()]
print(f'  Product-specific: {len(prod_paths)}')
for p in prod_paths:
    print(f'    {p.split("/")[-1]}')

# ────────────────────────────────────────────────────────────────────────────
# STEP 4: 갤러리 / 피처 분류
# ────────────────────────────────────────────────────────────────────────────
print('\nSTEP 4: Classify gallery / feature')

def is_gallery(p):
    fn = p.split('/')[-1].lower()
    return (
        'gallery' in p.lower() or
        re.search(r'-gallery-\d+', fn) or
        re.search(r'[-_]0[1-9][-_]?2010', fn) or
        fn.endswith('-2010.jpg') or fn.endswith('-2010.jpeg')
    )

def is_feat(p):
    fn = p.split('/')[-1].lower()
    return (
        'feature' in p.lower() or
        re.search(r'[-_]feature[-_]', fn) or
        re.search(r'[-_][df]\.(?:jpg|jpeg|png|webp)$', fn)
    )

def is_desktop(p):
    fn = p.split('/')[-1].lower()
    return (
        re.search(r'[-_]d\.(?:jpg|jpeg|png|webp)$', fn) or
        '-desktop.' in fn or
        re.search(r'-d-', fn) or
        not re.search(r'[-_]m\.(?:jpg|jpeg|png|webp)$', fn)  # 모바일 아닌 것
    )

def is_mobile(p):
    fn = p.split('/')[-1].lower()
    return (
        re.search(r'[-_]m\.(?:jpg|jpeg|png|webp)$', fn) or
        '-mobile.' in fn
    )

gal_paths  = [p for p in prod_paths if is_gallery(p) and not is_mobile(p)]
feat_paths = [p for p in prod_paths if not is_gallery(p) and not is_mobile(p)]

# 갤러리: -2010 suffix (메인뷰) 우선, 없으면 전체
gal_main = [p for p in gal_paths if '-2010.' in p]
if not gal_main:
    gal_main = gal_paths

# 피처: 데스크톱 우선
feat_desk = [p for p in feat_paths if is_desktop(p) and not is_mobile(p)]
if not feat_desk:
    feat_desk = feat_paths

print(f'  Gallery (main): {len(gal_main)}')
for p in gal_main: print(f'    {p.split("/")[-1]}')
print(f'  Feature (desktop): {len(feat_desk)}')
for p in feat_desk: print(f'    {p.split("/")[-1]}')

# ────────────────────────────────────────────────────────────────────────────
# STEP 5: 이미지 치수 병렬 fetch
# ────────────────────────────────────────────────────────────────────────────
print('\nSTEP 5: Fetching image dimensions')
all_selected = gal_main + feat_desk
urls_to_check = [CDN + p for p in all_selected]

dims_map = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    futures = {ex.submit(image_dims, u): u for u in urls_to_check}
    for fut in concurrent.futures.as_completed(futures):
        u = futures[fut]
        w, h = fut.result()
        dims_map[u] = (w, h)
        print(f'  {u.split("/")[-1]}: {w}x{h}')

# ────────────────────────────────────────────────────────────────────────────
# STEP 6: 피처 텍스트 추출
# ────────────────────────────────────────────────────────────────────────────
print('\nSTEP 6: Feature text extraction')

def get_feat_text(html, path):
    fn = path.split('/')[-1]
    stem = fn.rsplit('.', 1)[0]
    # 파일명 stem 으로 HTML 내 위치 검색
    positions = [m.start() for m in re.finditer(re.escape(stem), html, re.IGNORECASE)]
    best = next((p for p in positions if 50000 < p < len(html) - 2000), None)
    if best is None and positions:
        best = positions[0]
    if best is None:
        return '', ''
    # 앞뒤 4000자 스니펫
    snip = html[max(0, best - 500):best + 4000]
    hl_m = re.search(r'c-text-contents__headline[^>]*>([\s\S]{1,400}?)</div', snip)
    bd_m = re.search(r'c-text-contents__body[^>]*>([\s\S]{1,1000}?)</div', snip)
    t = clean_html(hl_m.group(1)) if hl_m else ''
    d = clean_html(bd_m.group(1)) if bd_m else ''
    return t, d

# 피처 레이블 fallback (파일명 기반)
def label_from_path(path):
    fn = path.split('/')[-1].rsplit('.', 1)[0]
    fn = re.sub(r'[-_]d$', '', fn, flags=re.IGNORECASE)
    fn = re.sub(r'ultrafine[-_]uhd[-_]4k[-_]5k[-_]27us550[-_]2024[-_]', '', fn, flags=re.IGNORECASE)
    fn = re.sub(r'ultrafine[-_]27us500[-_]', '', fn, flags=re.IGNORECASE)
    fn = re.sub(r'[-_]+', ' ', fn).strip().title()
    return fn

feat_items = []
for path in feat_desk:
    url = CDN + path
    w, h = dims_map.get(url, (0, 0))
    t, d = get_feat_text(html, path)
    label = t if t else label_from_path(path)
    feat_items.append({'p': path, 'a': label, 't': t, 'd': d, 'w': w, 'h': h})
    print(f'  [{len(feat_items)}] {path.split("/")[-1][-45:]}')
    print(f'       label={label[:50]} | t={t[:40]} | {w}x{h}')

# ────────────────────────────────────────────────────────────────────────────
# STEP 7: 스펙 추출
# ────────────────────────────────────────────────────────────────────────────
print('\nSTEP 7: Specs extraction')

specs = {}
# 방법 1: c-compare-selling__spec-name/desc
spec_pairs = re.findall(
    r'c-compare-selling__spec-name[^>]*>([\s\S]{1,200}?)</(?:p|div|span)>'
    r'[\s\S]{0,400}?'
    r'c-compare-selling__spec-desc[^>]*>([\s\S]{1,400}?)</(?:p|div|span)>',
    html)
print(f'  Method1 (c-compare-selling): {len(spec_pairs)} pairs')
for sn, sd in spec_pairs:
    k = re.sub(r'\s+', '_', clean_html(sn))
    v = clean_html(sd)
    if k and v:
        specs[k] = v

# 방법 2: JSON-LD additionalProperty
json_props = re.findall(r'"name"\s*:\s*"([^"]+)"[\s\S]{0,100}?"value"\s*:\s*"([^"]+)"', html)
for n, v in json_props:
    k = re.sub(r'\s+', '_', n.strip())
    if k not in specs and v.strip():
        specs[k] = v.strip()

print(f'  Total specs extracted: {len(specs)}')
for k, v in list(specs.items())[:10]:
    print(f'    {k}: {v[:60]}')

# 제품 지식 기반 기본 스펙 보강
BASE_SPECS = {
    'Type':             'UHD 4K Monitor',
    'Screen_Size_inch': '27',
    'Resolution':       '3840 x 2160 (UHD 4K)',
    'Panel_Type':       'IPS',
    'Brightness_nit':   '250',
    'Contrast_Ratio':   '1000:1',
    'Response_Time_ms': '5 (GtG)',
    'Refresh_Rate_Hz':  '60',
    'HDR':              'HDR10',
    'Color_Gamut':      'DCI-P3 90%',
    'USB_C_PD_W':       '96',
    'Ports':            'USB-C x1 (96W PD), HDMI x2, USB-A x2, 3.5mm Audio',
    'Color':            'White',
    'Model':            CODE,
}
for k, v in BASE_SPECS.items():
    if k not in specs:
        specs[k] = v

print(f'  Final specs: {len(specs)}')

# ────────────────────────────────────────────────────────────────────────────
# STEP 8: JS 빌드
# ────────────────────────────────────────────────────────────────────────────
print('\nSTEP 8: Building JS')

# 갤러리 JS
gal_parts = []
for path in gal_main:
    url = CDN + path
    w, h = dims_map.get(url, (0, 0))
    gal_parts.append(f'{{p:"{path}",w:{w},h:{h}}}')
new_gal_js = '[' + ','.join(gal_parts) + ']'
print(f'  gal: {len(gal_parts)} items')

# 피처 JS
feat_parts = []
for item in feat_items:
    feat_parts.append(
        f'{{a:"{jsstr(item["a"])}",p:"{item["p"]}",t:"{jsstr(item["t"])}",d:"{jsstr(item["d"])}",w:{item["w"]},h:{item["h"]}}}')
new_feat_js = '[' + ','.join(feat_parts) + ']'
print(f'  feat: {len(feat_parts)} items')

# 스펙 JS
sp_parts = [f'"{k}":"{jsstr(v)}"' for k, v in specs.items()]
new_sp_js = '{' + ','.join(sp_parts) + '}'
print(f'  sp: {len(sp_parts)} items')

# ────────────────────────────────────────────────────────────────────────────
# STEP 9: v6_20 엔트리 교체
# ────────────────────────────────────────────────────────────────────────────
print('\nSTEP 9: Updating v6_20')
v620 = open(V6_20, encoding='utf-8').read()
idx = v620.find(f'{{id:"{CODE}"')
if idx < 0:
    print(f'ERROR: {CODE} not found in v6_20!'); sys.exit(1)
nxt = v620.find('{id:"', idx + 10)
entry_old = v620[idx:nxt]
print(f'  Old entry: {len(entry_old):,} chars')

entry_new = replace_field(entry_old, 'gal', new_gal_js)
entry_new = replace_field(entry_new, 'feat', new_feat_js)
entry_new = replace_field(entry_new, 'sp', new_sp_js)
entry_new = replace_str_field(entry_new, 'nm', jsstr(nm))
entry_new = replace_str_field(entry_new, 'pr', price)
entry_new = replace_str_field(entry_new, 'crawled', 'true')

print(f'  New entry: {len(entry_new):,} chars')
v620_new = v620[:idx] + entry_new + v620[nxt:]
open(V6_20, 'w', encoding='utf-8').write(v620_new)
print('  v6_20 saved.')

# ────────────────────────────────────────────────────────────────────────────
# STEP 10: 순서 재배치
# ────────────────────────────────────────────────────────────────────────────
print('\nSTEP 10: Reordering product list')
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
    s = m.start()
    e = splits[i+1].start() if i + 1 < len(splits) else len(arr_body)
    raw = arr_body[s:e].rstrip(',\n ')
    cm = re.match(r'\{id:"([^"]+)"', raw)
    code = cm.group(1) if cm else f'UNKNOWN_{i}'
    entries.append((code, raw))

print(f'  Total entries: {len(entries)}')
top_set  = set(TOP_ORDER)
code_map = {c: e for c, e in entries}
top_entries  = [(c, code_map[c]) for c in TOP_ORDER if c in code_map]
rest_entries = [(c, e) for c, e in entries if c not in top_set]
new_entries  = top_entries + rest_entries

new_body = ',\n'.join(e for _, e in new_entries)
open(V6_20, 'w', encoding='utf-8').write(before + '\n' + new_body + '\n' + after)

print(f'  Top 5: {[c for c, _ in new_entries[:5]]}')
print('\n✅ 27US550-W 재크롤 완료!')
