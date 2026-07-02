"""
WFV1214BST1 v6_20 통합 스크립트
- wfv1214bst1_data.json에서 갤러리/스펙 로드
- 피처 텍스트를 HTML c-text-contents 구조로 정확 추출
- 기존 v6_20 엔트리의 amz_title/amz_desc/bul/faq/promo/disc/kw 보존
- gal / feat / sp / pr / nm 만 갱신
"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE     = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
HTML_SRC = f'{BASE}/bulk_html/WFV1214BST1.html'
V6_20    = f'{BASE}/LG_AI_Content_Hub_v6_20.html'
JSON_SRC = f'{BASE}/wfv1214bst1_data.json'
CODE     = 'WFV1214BST1'
PREFIX   = '/content/dam/channel/wcms/sa_en'

# ──────────────────────────────────────────────────────────
# 유틸
# ──────────────────────────────────────────────────────────
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

# ──────────────────────────────────────────────────────────
# 1. JSON 데이터 로드 (갤러리 + 스펙)
# ──────────────────────────────────────────────────────────
with open(JSON_SRC, encoding='utf-8') as f:
    raw = json.load(f)

gallery  = raw['gallery']   # {a, p, w, h}
specs    = raw['specs']     # {key: val}
price_raw = raw['price']    # e.g. "3649"
name_raw  = raw['name']

def fmt_price(v):
    try:
        f = float(v)
        return f'SAR {int(f):,}'
    except:
        return f'SAR {v}' if v else ''

price_fmt = fmt_price(price_raw)   # SAR 3,649

# ──────────────────────────────────────────────────────────
# 2. 피처 텍스트 - HTML c-text-contents 직접 파싱
# ──────────────────────────────────────────────────────────
html = open(HTML_SRC, encoding='utf-8', errors='replace').read()

# 피처 이미지 순서 (PDP 순서 유지)
FEAT_FILES = [
    # (desktop_filename, fallback_title, fallback_desc)
    ('WD-Vivace-V700-VC3-VCM-01-1-Vivace-Intro-Desktop.jpg',
     'VIVACE — Next-Gen Front Load Performance',
     'The LG VIVACE 12 kg front-load washer combines advanced AI technology, premium Black Steel finish and a refined tempered-glass door in a 600 × 850 × 610 mm chassis.'),

    ('WD-Vivace-V900-VC2-BlackSteel-02-1-AIDD-Desktop.gif',
     'Intelligent Care with 18% More Fabric Protection',
     'Based on big data of accumulated washing experience, AI DD® offers the most optimised washing motion to care for your laundry.'),

    ('WD-Vivace-V900-VC2-BlackSteel-03-AIDD-info-Desktop.jpg',
     'What is AI DD®?',
     'AI DD® detects not only the weight, but also senses the softness of fabric, and it chooses the optimal wash motion from 6 Motion DD patterns.'),

    ('WD-Vivace-V700-VC3-VCM-05-TurboWash-Desktop.jpg',
     'Less Time, More Life',
     'TurboWash™ technology cleans your clothes in 39 minutes. Spend less time on laundry and more time living.'),

    ('WD-Vivace-V900-VC2-BlackSteel-05-1-TurboWash-360-Desktop.jpg',
     'TurboWash™ 360° Multi-Directional Spray',
     'TurboWash™ with multi-directional spray rinses detergent through fabrics faster for a deep clean in less time.'),

    ('WD-Vivace-V900-VC2-BlackSteel-07-1-Steam-Plus-Desktop.jpg',
     'Less Wrinkles, More Hygienic',
     'LG Steam® technology eliminates 99.9% of allergens such as dust mites that can cause allergy or respiratory problems, while reducing wrinkles by up to 30%.'),

    ('WD-Vivace-V900-VC2-BlackSteel-07-2-Steam-Plus-Desktop.jpg',
     'Steam+ Allergen Care',
     'True Steam+ penetrates fibres deeply to remove allergens and leave clothes fresher with fewer wrinkles after every wash.'),

    ('WD-Vivace-V900-VC2-BlackSteel-08-Steam-Plus-info-Desktop.jpg',
     '30% Less Wrinkles',
     'The wrinkles formed during spin dehydration disappear through the Steam+ tumble motion, delivering clothes that are ready to wear.'),

    ('WD-Vivace-V900-VC2-BlackSteel-09-Steam-Plus-info-Desktop.jpg',
     '99.9% Allergen Removal',
     'Allergens reduced up to 99.9% by Steam+. Certified care for bedding, baby laundry and delicates.'),

    ('WD-Vivace-V700-VC3-VCM-09-1-Bigger-Capacity-Desktop.gif',
     'Bigger Capacity in the Same Space',
     'Get a bigger drum capacity in the same external size — more laundry done per cycle without changing your laundry room layout.'),

    ('WD-Vivace-V900-VC2-BlackSteel-10-1-Bigger-Capacity-Desktop.gif',
     '12 kg XL Drum — Standard 600 mm Width',
     "LG's redesigned drum packs a 12 kg wash load into the standard 600 mm wide footprint every laundry room is already built for."),

    ('WM-Vivace-V700-VC3-White-09-1-Druability-Desktop.jpg',
     'More Durable and Hygienic',
     'Boosted external durable design with an elegant tempered glass door and a developed hygienic full stainless-steel drum for reliable long-term performance.'),

    ('WM-Vivace-V700-VC3-VCM-10-Design-Desktop.jpg',
     'More Visible and Elegant',
     'More visible display and increased knob size with a metallic finish — premium aesthetics that complement any laundry room.'),

    ('WD-Vivace-V700-VC3-White-12-1-Compatibility-Desktop.jpg',
     'Available with TWINWash™ Mini',
     'Add a TWINWash™ Mini according to your preferences to suit your lifestyle and interior design needs — two loads washed simultaneously.'),

    ('WM-Vivace-V700-VC3-VCM-12-1-ThinQ-Desktop.jpg',
     'Smart Appliance',
     'With ThinQ® technology, your washer just got smarter — from operating your laundry remotely to downloading new wash cycles.'),

    ('WD-Vivace-V900-VC2-BlackSteel-14-1-SmartThinQ-Desktop.jpg',
     'LG ThinQ® — Control from Anywhere',
     'Remotely start, stop and monitor cycles. Run Smart Diagnosis™ from your phone. Compatible with Amazon Alexa and Google Assistant.'),

    ('WM-Vivace-V700-VC3-White-01-2-Vivace-Intro-Desktop.jpg',
     'VIVACE Series — Refined Elegance',
     'The VIVACE series brings next-generation motor performance and premium aesthetics together in one whisper-quiet, energy-efficient package.'),
]

def get_feat_text(fn):
    """c-text-contents__headline + body 파싱, 없으면 alt 텍스트."""
    stem = fn.rsplit('.', 1)[0]
    # PDP 본문 영역에서 탐색 (JSON-LD 구간 제외)
    all_pos = [m.start() for m in re.finditer(re.escape(stem), html)]
    best_pos = None
    for pos in all_pos:
        if 150000 < pos < 600000:
            best_pos = pos
            break
    if best_pos is None:
        return '', '', ''
    snip = html[best_pos:best_pos + 3000]
    alt_m  = re.search(r'alt="([^"]{5,120})"', snip)
    hl_m   = re.search(r'c-text-contents__headline[^>]*>([\s\S]{1,400}?)</div>', snip)
    bd_m   = re.search(r'c-text-contents__body[^>]*>([\s\S]{1,600}?)</div>', snip)
    alt    = clean(alt_m.group(1))  if alt_m else ''
    title  = clean(hl_m.group(1))  if hl_m else ''
    desc   = clean(bd_m.group(1))  if bd_m else ''
    return alt, title, desc

features_out = []
for fn, fb_title, fb_desc in FEAT_FILES:
    full_path = f'{PREFIX}/images/wm/features/{fn}'
    rel_path  = f'/images/wm/features/{fn}'
    # dimensions from JSON
    match_feat = next((f for f in raw['features'] if fn in f['p']), None)
    w = match_feat['w'] if match_feat else 0
    h = match_feat['h'] if match_feat else 0

    alt, title, desc = get_feat_text(fn)

    # 제목/설명이 없거나 파일명 그대로인 경우 fallback 사용
    if not title or len(title) < 5 or re.search(r'^(WD|WM)-Vivace', title):
        title = fb_title
    if not desc or len(desc) < 10:
        desc = fb_desc

    # alt → 섹션 레이블
    label = alt if alt and not re.search(r'^(WD|WM)-Vivace|White-01', alt) else fn.rsplit('.', 1)[0].split('-Desktop')[0].split('-')[-1].title()

    features_out.append({
        'a': label or 'Feature',
        'p': rel_path,
        't': title,
        'd': desc,
        'w': w,
        'h': h,
    })

print(f'Features built: {len(features_out)}')
for i, f in enumerate(features_out):
    print(f'  [{i+1:02d}] {f["a"][:30]:30} {f["w"]}x{f["h"]}  T: {f["t"][:60]}')

# ──────────────────────────────────────────────────────────
# 3. JS 배열 생성
# ──────────────────────────────────────────────────────────
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

print(f'\nGallery  JS: {len(gal_js):,} chars ({len(gallery)} imgs)')
print(f'Features JS: {len(feat_js):,} chars ({len(features_out)} imgs)')
print(f'Specs    JS: {len(specs_js):,} chars ({len(specs)} keys)')

# ──────────────────────────────────────────────────────────
# 4. v6_20 엔트리 갱신
# ──────────────────────────────────────────────────────────
with open(V6_20, 'r', encoding='utf-8') as f:
    v620 = f.read()

# WFV1214BST1 엔트리 위치 확인
entry_start = v620.find(f'{{id:"{CODE}"')
if entry_start < 0:
    print('ERROR: entry not found')
    sys.exit(1)

# 엔트리 끝 탐색 (다음 {id: 또는 ]; 전까지)
entry_end_m = re.search(r'},\s*\{id:', v620[entry_start:])
if entry_end_m:
    entry_end = entry_start + entry_end_m.start() + 1  # ',' 직전까지
else:
    entry_end = v620.find('];', entry_start)
    if entry_end < 0:
        print('ERROR: cannot find entry end')
        sys.exit(1)

entry_old = v620[entry_start:entry_end]
print(f'\nOld entry: {len(entry_old):,} chars')

# gal, feat, sp 교체 (정규식으로 개별 필드 교체)
def replace_field(entry, field, new_val):
    """entry 문자열에서 field:... 를 새 값으로 교체."""
    # gal:[...] / feat:[...] / sp:{...}
    pat = re.compile(
        r'(?<=[,{])\s*' + re.escape(field) + r'\s*:\s*'
        + r'(\[[\s\S]*?\]|\{[\s\S]*?\})',
        re.DOTALL
    )
    m = pat.search(entry)
    if not m:
        print(f'  WARNING: field "{field}" not found')
        return entry
    return entry[:m.start(1)] + new_val + entry[m.end(1):]

# nm, pr 업데이트 (기존 것보다 더 완전한 이름인 경우)
def replace_str_field(entry, field, new_val):
    pat = re.compile(r'(?<=[,{])(' + re.escape(field) + r':")([^"]*?)(")')
    m = pat.search(entry)
    if not m:
        print(f'  WARNING: str field "{field}" not found')
        return entry
    return entry[:m.start(2)] + jsstr(new_val) + entry[m.end(2):]

entry_new = entry_old
entry_new = replace_field(entry_new, 'gal',  gal_js)
entry_new = replace_field(entry_new, 'feat', feat_js)
entry_new = replace_field(entry_new, 'sp',   specs_js)
entry_new = replace_str_field(entry_new, 'pr', price_fmt)

print(f'New entry: {len(entry_new):,} chars')

v620_new = v620[:entry_start] + entry_new + v620[entry_end:]

# 백업
import shutil, os
bak = f'{BASE}/LG_AI_Content_Hub_v6_20.backup.html'
if not os.path.exists(bak):
    shutil.copy(V6_20, bak)
    print(f'Backup: {bak}')

with open(V6_20, 'w', encoding='utf-8') as f:
    f.write(v620_new)

print(f'\n✅ v6_20 updated: {len(v620_new):,} chars')
print(f'   Gallery  : {len(gallery)} images (was 6)')
print(f'   Features : {len(features_out)} images (was 8)')
print(f'   Specs    : {len(specs)} items')
print(f'   Price    : {price_fmt}')
