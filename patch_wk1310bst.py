"""WK1310BST 패치: 갤러리 정제 + 스펙 추출 + 피처 선별 후 v6_20 재통합"""
import re, json, sys, io, urllib.request, concurrent.futures as cf
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE    = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
HTML_SRC = f'{BASE}/bulk_html/WK1310BST.html'
V6_20   = f'{BASE}/LG_AI_Content_Hub_v6_20.html'
CODE    = 'WK1310BST'
PREFIX  = '/content/dam/channel/wcms/sa_en'
UA      = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

html = open(HTML_SRC, encoding='utf-8', errors='replace').read()

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

# ── 1. 스펙 (WashTower c-icon-block 구조) ──────────────────
blocks = re.findall(
    r'c-icon-block-contents[^>]*>[\s\S]{1,300}?'
    r'c-text-contents__headline[\s\S]{1,200}?'
    r'<strong[^>]*>([\s\S]{2,60}?)</strong>'
    r'[\s\S]{1,400}?'
    r'c-text-contents__bodycopy[\s\S]{1,100}?'
    r'<div class="cmp-text"[^>]*>([\s\S]{1,100}?)</div>',
    html)
specs = {}
for k, v in blocks:
    k = clean(k).rstrip(':'); v = clean(v)
    if k and v and k not in specs:
        specs[k[:50]] = v[:150]
print(f'Specs: {len(specs)}')
for k, v in specs.items():
    print(f'  {k}: {v}')

# ── 2. 갤러리: 1600x1062 사이즈 11컷만 ────────────────────
gal_paths = sorted(set(re.findall(
    r'/content/dam/channel/wcms/sa_en/images/washing-machines/wk1310bst[^"]+/gallery/1600x1062-\d+\.jpg',
    html)))
print(f'\nGallery (1600x1062): {len(gal_paths)}')
for g in gal_paths:
    print(f'  {g.split("/")[-1]}')

# ── 3. 피처: 주요 섹션 이미지 선별 ────────────────────────
# 번호별로 핵심 피처만 유지 (intro, AI, allergy, turbowash, centre-control, 설치 등)
FEAT_PLAN = [
    # (rel_path, fallback_title, fallback_desc)
    ('/images/wm/wd-washtower-24-Platinum-Black-2023-01-Thumbnail-desktop.jpg',
     'LG WashTower™ — All-in-One Laundry Solution',
     'The LG WashTower™ integrates a 13kg washer and 10kg dryer in a single sleek unit — saving space without compromising capacity or performance.'),

    ('/images/wm/wd-washtower-24-Platinum-Black-2023-05-1-desktop.jpg',
     'Centre Control™ — Intuitive Single Panel',
     'The Centre Control™ panel sits at eye level between the washer and dryer, giving you full command of both machines from one convenient interface.'),

    ('/images/wm/wd-washtower-24-Platinum-Black-2023-05-2-desktop.jpg',
     'Space-Saving Design',
     'WashTower™ combines washer and dryer in a compact vertical stack — ideal for any interior and freeing up valuable floor space.'),

    ('/images/wm/wd-washtower-24-Platinum-Black-2023-05-3-desktop.jpg',
     'Fabric Care Intelligence',
     'AI-powered fabric care technology detects your laundry type and automatically selects the optimal wash and dry settings for every load.'),

    ('/images/wm/wd-washtower-24-Platinum-Black-2023-05-4-desktop.jpg',
     'Time-Saving Performance',
     'WashTower™ is suitable for any interior and makes your space look more elegant and saves time.'),

    ('/images/wm/wd-washtower-24-Platinum-Black-2023-06-desktop.jpg',
     'Premium Black Steel Finish',
     'The sleek Black Steel finish and seamless design make WashTower™ a statement piece in any laundry room or living space.'),

    ('/images/wm/wd-washtower-24-Platinum-Black-2023-09-2-desktop.jpg',
     'Auto Sense AI DD™ — Built-in Intelligence',
     'Auto Sense AIDD™ technology detects the most suitable wash cycle based on fabric type and load weight — taking out the guesswork automatically.'),

    ('/images/wm/wd-washtower-24-Platinum-Black-2023-11-thumbnail-desktop.jpg',
     'Synced Washing and Drying Cycles',
     'The drying cycle syncs automatically with the washing cycle selected — dryer settings are chosen based on what you washed for a perfectly matched result.'),

    ('/images/wm/wd-washtower-24-Platinum-Black-2023-13-thumbnail-desktop.jpg',
     'Built-in Intelligence Takes Out the Guesswork',
     'Auto Sense AIDD™ technology detects the most suitable wash cycle to handle your laundry needs — no manual selection required.'),

    ('/images/wm/wd-washtower-24-Platinum-Black-2023-15-1-desktop.jpg',
     'Complete Washing and Drying in an Hour',
     'The dryer starts to pre-heat before the end of washing, so drying takes less time — complete washing and drying in just one hour.'),

    ('/images/wm/wd-washtower-24-Platinum-Black-2023-18-thumbnail-desktop.jpg',
     'Get Your Laundry Done in Less Time',
     'Your laundry can be thoroughly cleaned in just 39 minutes without compromising fabric care — TurboWash™ technology delivers speed and quality.'),

    ('/images/wm/wd-washtower-24-Platinum-Black-2023-25-thumbnail-desktop.jpg',
     'LG ThinQ® Smart Control',
     'Monitor and control your WashTower™ remotely via the LG ThinQ® app — start, pause and receive notifications from anywhere.'),

    ('/images/wm/wd-washtower-24-Platinum-Black-2023-28-thumbnail-desktop.jpg',
     'Smart Pairing — Washer & Dryer Sync',
     'WashTower™ intelligently pairs washer and dryer cycles so they work in harmony — maximum efficiency with minimal effort.'),

    ('/images/wm/wd-washtower-24-Platinum-Black-2023-30-2-3-desktop.jpg',
     'Efficient Product Maintenance',
     'The LG ThinQ™ app continuously monitors your washer — whether it\'s everyday maintenance or a quick troubleshoot, smart care is always at hand.'),

    ('/images/wm/wd-washtower-heat-pump-blacksteel-05-2-1-allergy-care-washer-d.jpg',
     'Allergy Care — Washer',
     'The Allergy Care wash cycle uses steam technology to eliminate 99.9% of allergens from fabrics — ideal for sensitive skin and baby garments.'),

    ('/images/wm/wd-washtower-heat-pump-blacksteel-05-2-2-allergy-care-dryer-d.jpg',
     'Allergy Care — Dryer',
     'The Allergy Care dry cycle uses high heat to reduce 99.9% of bacteria — delivering hygienically clean, allergen-free laundry every time.'),
]

# ── 4. 피처 텍스트 HTML 파싱 ──────────────────────────────
def get_feat_text(fn):
    stem = fn.rsplit('.', 1)[0]
    all_pos = [m.start() for m in re.finditer(re.escape(stem), html)]
    best = next((p for p in all_pos if 150000 < p < 700000), None)
    if best is None and all_pos: best = all_pos[0]
    if best is None: return '', '', ''
    snip = html[best:best + 3500]
    alt_m = re.search(r'alt="([^"]{5,120})"', snip)
    hl_m  = re.search(r'c-text-contents__headline[^>]*>([\s\S]{1,400}?)</div>', snip)
    bd_m  = re.search(r'c-text-contents__body[^>]*>([\s\S]{1,600}?)</div>', snip)
    return (clean(alt_m.group(1)) if alt_m else '',
            clean(hl_m.group(1))  if hl_m else '',
            clean(bd_m.group(1))  if bd_m else '')

# ── 5. Dimensions ─────────────────────────────────────────
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
                mk = data[i+1]
                if 0xC0 <= mk <= 0xCF and mk not in (0xC4, 0xC8, 0xCC):
                    return (data[i+7] << 8) | data[i+8], (data[i+5] << 8) | data[i+6]
                i += 2 + ((data[i+2] << 8) | data[i+3])
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return int.from_bytes(data[16:20], 'big'), int.from_bytes(data[20:24], 'big')
    except: pass
    return 0, 0

feat_paths = [fp for fp, _, _ in FEAT_PLAN]
gal_rel    = [g[len(PREFIX):] if g.startswith(PREFIX) else g for g in gal_paths]

all_fetch = [(g, 'gal') for g in gal_rel] + [(fp, 'feat') for fp in feat_paths]
dim_map = {}

print(f'\nFetching dimensions for {len(all_fetch)} images...')
def get_dim(t):
    p, k = t
    if p.lower().endswith('.gif'): return p, 1600, 900
    w, h = image_dims(p)
    return p, w, h

with cf.ThreadPoolExecutor(max_workers=20) as ex:
    for p, w, h in ex.map(get_dim, all_fetch):
        dim_map[p] = (w, h)
        tag = 'G' if (p, 'gal') in all_fetch else 'F'
        print(f'  {tag} {w:>5}x{h:<5}  {p.split("/")[-1]}')

# ── 6. 갤러리 label ───────────────────────────────────────
def gal_label(p):
    nm = p.split('/')[-1].lower()
    m = re.search(r'1600x1062-(\d+)', nm)
    return f'View {int(m.group(1))}' if m else 'Detail'

# ── 7. 피처 구성 ──────────────────────────────────────────
gallery_out = [{'a': gal_label(g), 'p': g, 'w': dim_map.get(g,(0,0))[0], 'h': dim_map.get(g,(0,0))[1]}
               for g in gal_rel]

features_out = []
for fp, fb_title, fb_desc in FEAT_PLAN:
    fn = fp.split('/')[-1]
    _, title_html, desc_html = get_feat_text(fn)
    title = title_html if title_html and len(title_html) > 5 else fb_title
    desc  = desc_html  if desc_html  and len(desc_html) > 10 else fb_desc
    # label from filename
    base  = fn.rsplit('.', 1)[0]
    nm_m  = re.search(r'2023-(\d+[-\d]*)-?(\w+?)-desktop$', base, re.I)
    if nm_m:
        label = nm_m.group(2).replace('-', ' ').title()
    else:
        allergy_m = re.search(r'allergy-care-(washer|dryer)', base, re.I)
        label = f'Allergy Care ({allergy_m.group(1).title()})' if allergy_m else fb_title[:30]
    w, h = dim_map.get(fp, (0, 0))
    features_out.append({'a': label, 'p': fp, 't': title, 'd': desc, 'w': w, 'h': h})

print(f'\nGallery  : {len(gallery_out)} images')
print(f'Features : {len(features_out)} images')
for i, f in enumerate(features_out):
    print(f'  [{i+1:02d}] {f["a"][:30]:30} {f["w"]}x{f["h"]}  T: {f["t"][:55]}')

# ── 8. JS 생성 ────────────────────────────────────────────
def js_gal(items):
    return '[' + ','.join(
        f'{{a:"{jsstr(g["a"])}",p:"{jsstr(g["p"])}",w:{g["w"]},h:{g["h"]}}}'
        for g in items) + ']'

def js_feat(items):
    parts = []
    for f in items:
        wh = f',w:{f["w"]},h:{f["h"]}' if f.get('w') and f.get('h') else ''
        parts.append(f'{{a:"{jsstr(f["a"])}",p:"{jsstr(f["p"])}",t:"{jsstr(f["t"])}",d:"{jsstr(f["d"])}"{wh}}}')
    return '[' + ','.join(parts) + ']'

def js_sp(sp):
    parts = []
    for k, v in sp.items():
        key = re.sub(r'[^A-Za-z0-9]', '_', k).strip('_')[:30]
        if not key or key[0].isdigit(): key = 'K_' + key
        parts.append(f'"{key}":"{jsstr(v)}"')
    return '{' + ','.join(parts) + '}'

gal_js  = js_gal(gallery_out)
feat_js = js_feat(features_out)
sp_js   = js_sp(specs)

# ── 9. v6_20 갱신 ─────────────────────────────────────────
with open(V6_20, 'r', encoding='utf-8') as f:
    v620 = f.read()

entry_start = v620.find(f'{{id:"{CODE}"')
if entry_start < 0: print('ERROR: entry not found'); exit(1)
entry_end = v620.find('{id:"', entry_start + 10)
entry_old = v620[entry_start:entry_end]

def replace_field(entry, field, new_val):
    pat = re.compile(
        r'(?<=[,{])\s*' + re.escape(field) + r'\s*:\s*(\[[\s\S]*?\]|\{[\s\S]*?\})',
        re.DOTALL)
    m = pat.search(entry)
    if not m: print(f'  WARNING: {field} not found'); return entry
    return entry[:m.start(1)] + new_val + entry[m.end(1):]

def replace_str(entry, field, new_val):
    pat = re.compile(r'(?<=[,{])(' + re.escape(field) + r':")([^"]*?)(")')
    m = pat.search(entry)
    if not m: print(f'  WARNING: str {field} not found'); return entry
    return entry[:m.start(2)] + jsstr(new_val) + entry[m.end(2):]

entry_new = entry_old
entry_new = replace_field(entry_new, 'gal',  gal_js)
entry_new = replace_field(entry_new, 'feat', feat_js)
entry_new = replace_field(entry_new, 'sp',   sp_js)
entry_new = replace_str(entry_new, 'pr', 'SAR 7,799')

v620_new = v620[:entry_start] + entry_new + v620[entry_end:]
with open(V6_20, 'w', encoding='utf-8') as f:
    f.write(v620_new)

print(f'\nOld entry: {len(entry_old):,} chars  →  New: {len(entry_new):,} chars')
print(f'✅ v6_20 updated!')
print(f'   Gallery  : {len(gallery_out)} (was 44 → 정제 11)')
print(f'   Features : {len(features_out)} (was 0)')
print(f'   Specs    : {len(specs)}')
print(f'   Price    : SAR 7,799')
