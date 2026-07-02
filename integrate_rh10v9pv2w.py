"""
RH10V9PV2W v6_20 통합 스크립트
- /wm/ 폴더 + rh90 공유 피처 포함
- 갤러리 14장 + 피처 16장 + 스펙 21개
- 기존 amz/bul/faq/promo/disc/kw 보존, gal/feat/sp/pr 갱신
"""
import re, json, sys, io, urllib.request, concurrent.futures as cf
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE     = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
HTML_SRC = f'{BASE}/bulk_html/RH10V9PV2W.html'
JSON_SRC = f'{BASE}/rh10v9pv2w_data.json'
V6_20    = f'{BASE}/LG_AI_Content_Hub_v6_20.html'
CODE     = 'RH10V9PV2W'
PREFIX   = '/content/dam/channel/wcms/sa_en'
UA       = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

def clean(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    s = (s.replace('&#x27;', "'").replace('&amp;', '&').replace('&quot;', '"')
          .replace('&nbsp;', ' ').replace('\u2122', '™').replace('\u00ae', '®')
          .replace('\u201c', '"').replace('\u201d', '"')
          .replace('\u2018', "'").replace('\u2019', "'")
          .replace('\\r', '').replace('\\n', ' ').replace('\\t', ' '))
    return re.sub(r'\s+', ' ', s).strip()

def jsstr(s):
    if s is None: s = ''
    s = str(s)
    s = (s.replace('\u201c', '"').replace('\u201d', '"')
          .replace('\u2018', "'").replace('\u2019', "'")
          .replace('\u2122', '™').replace('\u00ae', '®'))
    s = s.replace('\\', '\\\\').replace('"', '\\"')
    s = s.replace('\n', ' ').replace('\r', '').replace('\t', ' ')
    return re.sub(r'\s+', ' ', s).strip()

html = open(HTML_SRC, encoding='utf-8', errors='replace').read()

# ── 1. JSON 로드 (갤러리 + 스펙 + 가격) ────────────────────
with open(JSON_SRC, encoding='utf-8') as f:
    raw = json.load(f)

gallery = raw['gallery']   # large01~14, 1600×1062
specs   = raw['specs']
price   = raw['price']     # "3898.99"

def fmt_price(v):
    try:
        f = float(v)
        # 소수점 없으면 정수 포맷
        if f == int(f): return f'SAR {int(f):,}'
        return f'SAR {f:,.2f}'
    except:
        return f'SAR {v}' if v else ''

price_fmt = fmt_price(price)   # SAR 3,898.99

# ── 2. 피처 목록 (PDP 순서, 데스크탑 한정) ─────────────────
# (rel_path, fallback_title, fallback_desc)
FEAT_FILES = [
    # /wm/ 폴더 - 메인 피처
    ('/images/wm/Dryer-NA-Vivace-V900-VC2-HP-VCM-01-Intro-D.jpg',
     'For Consistent Performance, Sustainable Care',
     'LG DUAL Inverter Heat Pump™ Dryer delivers consistent, gentle drying performance with up to 65% energy savings — care your clothes can count on, cycle after cycle.'),

    ('/images/wm/Dryer-NA-Vivace-V900-VC2-HP-VCM-02-Dual-Inverter-Heat-Pump-D.jpg',
     'A Dry that Gives You Total Confidence',
     'Awarded the ENERGY STAR® Most Efficient Mark. Up to 65% energy saving with DUAL Inverter Heat Pump™ technology — exceptional drying results at lower temperatures that protect your garments.'),

    ('/images/wm/Dryer-NA-Vivace-V900-VC2-HP-VCM-03-Allergy-Care-D.jpg',
     'Reduce 99.9% of Bacteria',
     'The Allergy Care cycle uses high heat to reduce 99.9% of bacteria and allergens, giving you cleaner, fresher laundry with every load — ideal for baby clothes and bedding.'),

    ('/images/wm/Dryer-NA-Vivace-V900-VC2-HP-VCM-04-Dual-Filter-D.jpg',
     'Dual Filter — Twice the Clean',
     'Minimize lint and dust with the Dual Filter to the point where hair can\'t pass through — keeping the drum clean and your clothes lint-free.'),

    ('/images/wm/Dryer-NA-Vivace-V900-VC2-HP-VCM-05-Sensor-Dry-D.gif',
     'An Optimal Dry on the First Try',
     'Sensor Dry automatically optimises drying time using a humidity sensor — so clothes come out perfectly dry every time, with no over-drying or shrinkage.'),

    ('/images/wm/Dryer-NA-Vivace-V900-VC2-HP-VCM-06-Auto-Cleaning-Condenser-D.jpg',
     'Condenser with Convenient Cleaning',
     'The Auto Cleaning Condenser self-cleans so you don\'t have to — enjoy hassle-free maintenance and sustained peak efficiency without lifting a finger.'),

    # rh90 공유 피처 - Heat Pump 비교
    ('/images/dryers/rh90v9pv8w_aptgnag_emgf_sa_en_c/features/D09-01_Dryer-NA-Vivace-V900-VC2-HP-VCM-07-1-Conventional-D.jpg',
     'Conventional vs. DUAL Inverter Heat Pump™',
     'Side-by-side comparison shows how DUAL Inverter Heat Pump™ technology delivers superior drying results at lower temperatures versus conventional electric dryers.'),

    ('/images/dryers/rh90v9pv8w_aptgnag_emgf_sa_en_c/features/D09-02_Dryer-NA-Vivace-V900-VC2-HP-VCM-07-2-Inverter-HP-D.jpg',
     'Clothes Come Out Looking Like the Day You Bought Them',
     'DUAL Inverter Heat Pump™ uses lower drying temperatures to protect fabric quality — clothes maintain their shape, colour and texture wash after wash.'),

    # rh90 공유 피처 - ThinQ 스마트
    ('/images/dryers/rh90v9pv8w_aptgnag_emgf_sa_en_c/features/D11-01_Dryer-NA-Vivace-V900-VC2-HP-VCM-08-1-Remote-Control-D.jpg',
     'Drying Cycles That Fit Your Lifestyle',
     'With various drying cycles, you can properly dry your clothes and look great — then ready to go.'),

    ('/images/dryers/rh90v9pv8w_aptgnag_emgf_sa_en_c/features/D11-02_Dryer-NA-Vivace-V900-VC2-HP-VCM-08-2-Various-Cycle-D.jpg',
     'Pairing for More Intelligence',
     'With LG ThinQ®, the dryer automatically sets the proper dry cycle by receiving data from the LG washer — smart pairing for perfectly matched wash and dry every time.'),

    ('/images/dryers/rh90v9pv8w_aptgnag_emgf_sa_en_c/features/D11-03_Dryer-NA-Vivace-V900-VC2-HP-VCM-08-3-Smart-Pairing-D.jpg',
     'Put Your Dryer Anywhere',
     'Flexible installation options including pedestal, stacking or side-by-side let you place the dryer wherever suits your home best.'),

    # /wm/ 폴더 - 디자인/상세
    ('/images/wm/Dryer-NA-Vivace-V900-VC2-HP-VCM-09-1-Tempered-Glass-D.jpg',
     'Premium Tempered Glass Door',
     'The sleek tempered glass door adds a premium look while letting you monitor the drying cycle at a glance — robust, elegant and built to last.'),

    ('/images/wm/Dryer-NA-Vivace-V900-VC2-HP-VCM-09-3-Washer-Dryer-D.jpg',
     'Flexible Side-by-Side Pairing',
     'Place the dryer side by side with your LG washer for a coordinated laundry setup that maximises space and efficiency in any laundry room.'),

    ('/images/wm/Dryer-NA-Vivace-V900-VC2-HP-VCM-09-4-STS-Interior-D.jpg',
     'Full Stainless Steel Drum',
     'The full stainless steel drum interior is hygienic, corrosion-resistant and gentle on fabrics — ensuring consistent drying performance year after year.'),

    ('/images/wm/Dryer-NA-Vivace-V900-VC2-HP-VCM-09-5-Water-Drawer-D.jpg',
     'Convenient Water Drawer',
     'The top-mounted water drawer collects condensed water during the drying cycle — easy to remove and empty without interrupting your routine.'),

    ('/images/wm/Dryer-NA-Vivace-V900-VC2-HP-VCM-09-6-Pedestal-Installation-D.jpg',
     'Pedestal Installation Ready',
     'The optional pedestal raises the dryer to a comfortable working height and provides additional storage — perfect for a streamlined, ergonomic laundry room.'),
]

# ── 3. 피처 텍스트 추출 (HTML 파싱) ────────────────────────
def get_feat_text(fn):
    stem = fn.rsplit('.', 1)[0]
    all_pos = [m.start() for m in re.finditer(re.escape(stem), html)]
    best_pos = next((p for p in all_pos if 150000 < p < 700000), None)
    if best_pos is None and all_pos:
        best_pos = all_pos[0]
    if best_pos is None:
        return '', '', ''
    snip = html[best_pos:best_pos + 3500]
    alt_m = re.search(r'alt="([^"]{5,120})"', snip)
    hl_m  = re.search(r'c-text-contents__headline[^>]*>([\s\S]{1,400}?)</div>', snip)
    bd_m  = re.search(r'c-text-contents__body[^>]*>([\s\S]{1,600}?)</div>', snip)
    return (clean(alt_m.group(1)) if alt_m else '',
            clean(hl_m.group(1))  if hl_m else '',
            clean(bd_m.group(1))  if bd_m else '')

# ── 4. Dimensions 취득 ────────────────────────────────────
def image_dims(path):
    try:
        url = 'https://www.lg.com' + PREFIX + path
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Range': 'bytes=0-65536'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
        if data[:2] == b'\xff\xd8':
            i = 2
            while i < len(data) - 8:
                if data[i] != 0xFF: break
                marker = data[i+1]
                if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                    return ((data[i+7] << 8) | data[i+8], (data[i+5] << 8) | data[i+6])
                i += 2 + ((data[i+2] << 8) | data[i+3])
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return (int.from_bytes(data[16:20], 'big'), int.from_bytes(data[20:24], 'big'))
        if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            if b'VP8 ' in data[:40]:
                i2 = data.index(b'VP8 ')
                return (int.from_bytes(data[i2+14:i2+16], 'little') & 0x3FFF,
                        int.from_bytes(data[i2+16:i2+18], 'little') & 0x3FFF)
    except:
        pass
    return (0, 0)

print(f'Fetching dimensions for {len(FEAT_FILES)} feature images...')
feat_paths = [fp for fp, _, _ in FEAT_FILES]

dim_map = {}
# 갤러리는 이미 raw json에 있음
for g in gallery:
    dim_map[g['p']] = (g['w'], g['h'])

def get_dim(p):
    if p.lower().endswith('.gif'):
        return (p, 1600, 900)
    w, h = image_dims(p)
    return (p, w, h)

with cf.ThreadPoolExecutor(max_workers=16) as ex:
    for p, w, h in ex.map(get_dim, feat_paths):
        dim_map[p] = (w, h)
        print(f'  F {w:>5}x{h:<5}  {p.split("/")[-1]}')

# ── 5. features_out 구성 ───────────────────────────────────
features_out = []
for rel_path, fb_title, fb_desc in FEAT_FILES:
    fn = rel_path.split('/')[-1]
    _, title_html, desc_html = get_feat_text(fn)

    title = title_html if title_html and len(title_html) > 5 else fb_title
    desc  = desc_html  if desc_html  and len(desc_html) > 10 else fb_desc

    # label = 파일명에서 키워드 추출
    base  = fn.rsplit('.', 1)[0]
    # e.g. "Dryer-NA-Vivace-V900-VC2-HP-VCM-02-Dual-Inverter-Heat-Pump-D" → "Dual Inverter Heat Pump"
    kw_m  = re.search(r'VCM-\d+[-_]?\d*[-_]?([\w\-]+?)(?:[-_]D(?:\.|\b)|$)', base, re.I)
    label = kw_m.group(1).replace('-', ' ').replace('_', ' ').title() if kw_m else fb_title[:30]

    w, h = dim_map.get(rel_path, (0, 0))
    features_out.append({'a': label, 'p': rel_path, 't': title, 'd': desc, 'w': w, 'h': h})

print(f'\nFeatures built: {len(features_out)}')
for i, f in enumerate(features_out):
    print(f'  [{i+1:02d}] {f["a"][:32]:32} {f["w"]}x{f["h"]}  T: {f["t"][:55]}')

# ── 6. JS 문자열 생성 ─────────────────────────────────────
def js_arr_gal(items):
    parts = []
    for g in items:
        w = f',w:{g["w"]},h:{g["h"]}' if g.get('w') and g.get('h') else ''
        parts.append(f'{{a:"{jsstr(g["a"])}",p:"{jsstr(g["p"])}"{w}}}')
    return '[' + ','.join(parts) + ']'

def js_arr_feat(items):
    parts = []
    for f in items:
        w = f',w:{f["w"]},h:{f["h"]}' if f.get('w') and f.get('h') else ''
        parts.append(f'{{a:"{jsstr(f["a"])}",p:"{jsstr(f["p"])}",t:"{jsstr(f["t"])}",d:"{jsstr(f["d"])}"{w}}}')
    return '[' + ','.join(parts) + ']'

def js_obj_specs(sp):
    parts = []
    for k, v in sp.items():
        key = re.sub(r'[^A-Za-z0-9]', '_', k).strip('_')[:30]
        if not key or key[0].isdigit(): key = 'K_' + key
        parts.append(f'"{key}":"{jsstr(v)}"')
    return '{' + ','.join(parts) + '}'

gal_js   = js_arr_gal(gallery)
feat_js  = js_arr_feat(features_out)
specs_js = js_obj_specs(specs)

# ── 7. v6_20 갱신 ─────────────────────────────────────────
with open(V6_20, 'r', encoding='utf-8') as f:
    v620 = f.read()

entry_start = v620.find(f'{{id:"{CODE}"')
if entry_start < 0:
    print('ERROR: entry not found'); exit(1)
entry_end = v620.find('{id:"', entry_start + 10)
if entry_end < 0:
    entry_end = v620.find('];', entry_start)
entry_old = v620[entry_start:entry_end]
print(f'\nOld entry: {len(entry_old):,} chars')

def replace_field(entry, field, new_val):
    pat = re.compile(
        r'(?<=[,{])\s*' + re.escape(field) + r'\s*:\s*'
        + r'(\[[\s\S]*?\]|\{[\s\S]*?\})',
        re.DOTALL)
    m = pat.search(entry)
    if not m:
        print(f'  WARNING: field "{field}" not found'); return entry
    return entry[:m.start(1)] + new_val + entry[m.end(1):]

def replace_str_field(entry, field, new_val):
    pat = re.compile(r'(?<=[,{])(' + re.escape(field) + r':")([^"]*?)(")')
    m = pat.search(entry)
    if not m:
        print(f'  WARNING: str field "{field}" not found'); return entry
    return entry[:m.start(2)] + jsstr(new_val) + entry[m.end(2):]

entry_new = entry_old
entry_new = replace_field(entry_new, 'gal',  gal_js)
entry_new = replace_field(entry_new, 'feat', feat_js)
entry_new = replace_field(entry_new, 'sp',   specs_js)
entry_new = replace_str_field(entry_new, 'pr', price_fmt)

print(f'New entry: {len(entry_new):,} chars')

v620_new = v620[:entry_start] + entry_new + v620[entry_end:]

import shutil, os
bak = f'{BASE}/LG_AI_Content_Hub_v6_20.backup.html'
if not os.path.exists(bak):
    shutil.copy(V6_20, bak)

with open(V6_20, 'w', encoding='utf-8') as f:
    f.write(v620_new)

print(f'\n✅ v6_20 updated!')
print(f'   Gallery  : {len(gallery)} images (was 1)')
print(f'   Features : {len(features_out)} images (was 5, 잘못된 모델 참조)')
print(f'   Specs    : {len(specs)} items')
print(f'   Price    : {price_fmt}')
