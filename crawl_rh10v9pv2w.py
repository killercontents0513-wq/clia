"""
RH10V9PV2W 전체 재크롤 스크립트 (v6_20 통합용)
"""
import re, json, os, sys, io, urllib.request, concurrent.futures as cf
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE     = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
URL      = 'https://www.lg.com/sa_en/dryers/rh10v9pv2w/'
CODE     = 'RH10V9PV2W'
CAT      = 'Dryer'
SUB      = 'Heat Pump'
ICO      = '🌀'
DV       = 'HA'
PREFIX   = '/content/dam/channel/wcms/sa_en'
UA       = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
HTML_OUT = f'{BASE}/bulk_html/{CODE}.html'

EXCLUDE = [
    '/gnb/','/home-page/','/banners-20','/ai-core-tech','/2025-webos/webos-microsite',
    '/common-icon/','/elements/icons-line/','/members-offer','/multishop','/ministry-of',
    '/oled-speaker/gnb','/spring-sale','/next-day','/watch-it-promo','/av-wm-pto',
    '/bundles-jan','/buy-one-get','/alrajhi','/gnb-banner','/common/common-icon',
]

# ── 1. FRESH DOWNLOAD ──────────────────────────────────────
print(f'▶ Fetching {URL} ...')
req = urllib.request.Request(URL, headers={'User-Agent': UA})
with urllib.request.urlopen(req, timeout=40) as r:
    raw = r.read()
with open(HTML_OUT, 'wb') as f:
    f.write(raw)
html = raw.decode('utf-8', errors='replace')
print(f'  Downloaded: {len(html):,} chars')

# ── 2. JSON-LD 메타 ────────────────────────────────────────
def clean(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    s = (s.replace('&#x27;', "'").replace('&amp;', '&').replace('&quot;', '"')
          .replace('&nbsp;', ' ').replace('\u2122', '™').replace('\u00ae', '®')
          .replace('\u201c', '"').replace('\u201d', '"')
          .replace('\u2018', "'").replace('\u2019', "'")
          .replace('\\r', '').replace('\\n', ' ').replace('\\t', ' '))
    return re.sub(r'\s+', ' ', s).strip()

name, price, msrp = CODE, '', ''
for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL):
    try:
        d = json.loads(m.group(1))
        if isinstance(d, dict) and d.get('@type', '').lower() == 'product':
            name  = d.get('name') or name
            off   = d.get('offers') or {}
            if isinstance(off, dict):
                price = str(off.get('price') or '')
                psp   = off.get('priceSpecification') or {}
                if isinstance(psp, dict):
                    msrp = str(psp.get('price') or '')
    except:
        pass
print(f'  Name : {name}')
print(f'  Price: {price}  MSRP: {msrp}')

# ── 3. CDN 이미지 전수 추출 ────────────────────────────────
def excluded(p):
    pl = p.lower()
    return any(x in pl for x in EXCLUDE)

all_imgs = sorted(set(re.findall(
    r'/content/dam/channel/wcms/sa_en/[^"\'\ )]+?\.(?:jpg|jpeg|png|webp|gif)', html)))
all_imgs = [i for i in all_imgs
            if '/renditions/' not in i and '/jcr:content/' not in i and not excluded(i)]
print(f'\n  Total CDN images: {len(all_imgs)}')

from collections import Counter
folder_cnt = Counter()
for i in all_imgs:
    parts = i.rstrip('/').split('/')
    if len(parts) >= 4:
        folder_cnt['/'.join(parts[:-1])] += 1

code_l  = CODE.lower()
code_l2 = code_l.replace('-', '')
product_folders = set()
for folder, n in folder_cnt.items():
    fl = folder.lower()
    if code_l in fl or code_l2 in fl:
        product_folders.add(folder)
    elif n >= 6 and any(seg in fl for seg in [
        '/features/', '/gallery/', '/dryers/', '/wm/', '/ha/',
        '/washing-machines/', '/refrigerators/', '/vacuum', '/speakers/'
    ]):
        product_folders.add(folder)
for i in all_imgs:
    if code_l in i.lower() or code_l2 in i.lower():
        parts = i.rstrip('/').split('/')
        if len(parts) >= 4:
            product_folders.add('/'.join(parts[:-1]))

imgs = [i for i in all_imgs
        if '/'.join(i.rstrip('/').split('/')[:-1]) in product_folders]
seen = set()
imgs_dedup = []
for i in imgs:
    fn = i.split('/')[-1].lower()
    if fn not in seen:
        seen.add(fn)
        imgs_dedup.append(i)

print(f'  Product-specific images: {len(imgs_dedup)}')
print(f'  Product folders:')
for pf in sorted(product_folders):
    print(f'    {pf}  ({folder_cnt[pf]})')

# ── 4. 갤러리 vs 피처 분류 ────────────────────────────────
def is_feat(p):
    pl = p.lower()
    return 'feature' in pl or '/features/' in pl

def is_gal(p):
    pl = p.lower()
    nm = p.split('/')[-1].lower()
    if is_feat(p): return False
    if '/gallery/' in pl or '-gallery-' in pl: return True
    if re.match(r'^(d|dz|mz|s|z|l)[-_]?\d+\.', nm): return True
    if re.match(r'^\d{3}[\._]', nm): return True
    if 'basic' in nm or 'thumbnail' in nm or 'large' in nm: return True
    return False

gallery_raw  = [i for i in imgs_dedup if is_gal(i)]
features_raw = [i for i in imgs_dedup if is_feat(i)]

def is_desktop(p):
    return bool(re.search(r'(?:[-_]d(?:[-_]\d+)?\.|/desktop/|[-_]desktop[-._]|[-_]D\.)', p.lower()))
def is_mobile(p):
    return bool(re.search(r'[-_]m(?:obile)?(?:[-_]\d+)?\.|/mobile/|[-_]mobile[-.]', p.lower()))

desk = [i for i in features_raw if is_desktop(i)]
features_final = desk if len(desk) >= 3 else [i for i in features_raw if not is_mobile(i)] or features_raw

def gal_rank(p):
    nm = p.split('/')[-1].lower()
    if 'basic-large' in nm or 'large14' in nm or 'large' in nm: return 1
    if '2010' in nm: return 2
    if re.match(r'^dz[-_]', nm) or 'zoom' in nm: return 3
    if 'gallery-0' in nm or 'gallery_' in nm or '/gallery/' in p.lower(): return 4
    if re.match(r'^d[-_]\d+', nm): return 5
    if '450' in nm or 'basic' in nm: return 6
    if re.match(r'^z[-_]\d+', nm): return 4
    if re.match(r'^s[-_]', nm): return 8
    if re.match(r'^(mz|m)[-_]', nm): return 9
    if 'thumbnail' in nm: return 9
    return 7

gallery_sorted = sorted(gallery_raw, key=lambda p: (gal_rank(p), p))
def pos_key(p):
    nm = p.split('/')[-1].lower()
    m = re.search(r'(\d{1,2})(?=\.|[-_])', nm)
    return m.group(1).zfill(3) if m else nm
seen_pos = {}
gallery_final = []
for p in gallery_sorted:
    k = pos_key(p)
    if k not in seen_pos:
        seen_pos[k] = True
        gallery_final.append(p)

print(f'\n  Gallery  : {len(gallery_final)}')
for g in gallery_final:
    print(f'    {g}')
print(f'\n  Features : {len(features_final)}')
for f in features_final:
    print(f'    {f}')

# ── 5. Dimensions ─────────────────────────────────────────
def image_dims(path):
    try:
        url = 'https://www.lg.com' + path
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Range': 'bytes=0-65536'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
        if data[:2] == b'\xff\xd8':
            i = 2
            while i < len(data) - 8:
                if data[i] != 0xFF: break
                marker = data[i+1]
                if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                    h = (data[i+5] << 8) | data[i+6]
                    w = (data[i+7] << 8) | data[i+8]
                    return (w, h)
                seglen = (data[i+2] << 8) | data[i+3]
                i += 2 + seglen
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return (int.from_bytes(data[16:20], 'big'), int.from_bytes(data[20:24], 'big'))
        if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            if b'VP8 ' in data[:40]:
                idx2 = data.index(b'VP8 ')
                return (int.from_bytes(data[idx2+14:idx2+16], 'little') & 0x3FFF,
                        int.from_bytes(data[idx2+16:idx2+18], 'little') & 0x3FFF)
            if b'VP8L' in data[:40]:
                idx2 = data.index(b'VP8L')
                val = int.from_bytes(data[idx2+9:idx2+13], 'little')
                return ((val & 0x3FFF) + 1, ((val >> 14) & 0x3FFF) + 1)
    except:
        pass
    return (0, 0)

all_paths = [(p, 'gal') for p in gallery_final] + [(p, 'feat') for p in features_final]
dim_map = {}
print(f'\n  Fetching dimensions for {len(all_paths)} images...')

def get_dim(t):
    p, kind = t
    if p.lower().endswith('.gif'):
        return (p, 1600, 900)
    w, h = image_dims(p)
    return (p, w, h)

with cf.ThreadPoolExecutor(max_workers=20) as ex:
    for p, w, h in ex.map(get_dim, all_paths):
        dim_map[p] = (w, h)
        tag = 'G' if (p, 'gal') in all_paths else 'F'
        print(f'    {tag} {w:>5}x{h:<5}  {p.split("/")[-1]}')

# ── 6. 피처 텍스트 (c-text-contents 파싱) ─────────────────
def get_feat_text(fn):
    stem = fn.rsplit('.', 1)[0]
    all_pos = [m.start() for m in re.finditer(re.escape(stem), html)]
    best_pos = None
    for pos in all_pos:
        if 150000 < pos < 700000:
            best_pos = pos
            break
    if best_pos is None:
        return '', '', ''
    snip = html[best_pos:best_pos + 3500]
    alt_m = re.search(r'alt="([^"]{5,120})"', snip)
    hl_m  = re.search(r'c-text-contents__headline[^>]*>([\s\S]{1,400}?)</div>', snip)
    bd_m  = re.search(r'c-text-contents__body[^>]*>([\s\S]{1,600}?)</div>', snip)
    alt   = clean(alt_m.group(1)) if alt_m else ''
    title = clean(hl_m.group(1))  if hl_m else ''
    desc  = clean(bd_m.group(1))  if bd_m else ''
    return alt, title, desc

print('\n  Feature texts:')
feat_texts = []
for fp in features_final:
    fn = fp.split('/')[-1]
    alt, title, desc = get_feat_text(fn)
    feat_texts.append((fp, alt, title, desc))
    print(f'    [{fn[:45]}]')
    print(f'      alt  : {alt[:60]}')
    print(f'      title: {title[:70]}')
    print(f'      desc : {desc[:80]}')

# ── 7. 스펙 ───────────────────────────────────────────────
pairs = re.findall(
    r'c-compare-selling__spec-name"><p>([\s\S]*?)</p></div>'
    r'<div class="cmp-text c-compare-selling__spec-desc"><p>([\s\S]*?)</p>', html)
specs = {}
for k, v in pairs:
    k = clean(k).rstrip(':').strip()
    v = clean(v)
    if k and v and k not in specs:
        specs[k[:50]] = v[:200]
    if len(specs) >= 40: break
print(f'\n  Specs: {len(specs)}')
for k, v in specs.items():
    print(f'    {k}: {v}')

# ── 8. JSON 저장 ───────────────────────────────────────────
def rel(p):
    return p[len(PREFIX):] if p.startswith(PREFIX) else p

gallery_out  = [{'a': (lambda nm: (
    'Basic Large' if 'large' in nm else
    f'Zoom {int(re.match(r"^dz[-_]?(\d+)",nm).group(1))}' if re.match(r'^dz[-_]?(\d+)',nm) else
    f'View {int(re.match(r"^[a-z]+[-_]?(\d+)",nm).group(1))}' if re.match(r'^[a-z]+[-_]?(\d+)',nm) else
    f'Gallery {int(re.search(r"gallery[-_]?(\d+)",nm).group(1))}' if re.search(r'gallery[-_]?(\d+)',nm) else
    f'View {int(re.search(r"(\d+)",nm).group(1))}' if re.search(r'(\d+)',nm) else 'Detail'
))(g.split('/')[-1].lower()),
    'p': rel(g), 'w': dim_map.get(g,(0,0))[0], 'h': dim_map.get(g,(0,0))[1]}
    for g in gallery_final]

features_out = []
for fp, alt, title, desc in feat_texts:
    fn   = fp.split('/')[-1]
    base = fn.rsplit('.', 1)[0]
    am   = re.search(r'(\d+[-_]?\d*[-_]?[a-z0-9\-]*?)(?:[-_]d(?:esktop)?|$)', base, re.I)
    label = alt if alt and len(alt) > 3 else (am.group(1) if am else base[:20]).replace('-',' ').replace('_',' ').strip().title()
    w, h = dim_map.get(fp, (0, 0))
    features_out.append({'a': label, 'p': rel(fp), 't': title or label, 'd': desc or title or '', 'w': w, 'h': h})

result = {
    'code': CODE, 'cat': CAT, 'sub': SUB, 'ico': ICO, 'dv': DV, 'url': URL,
    'name': name, 'price': price, 'msrp': msrp,
    'gallery': gallery_out, 'features': features_out, 'specs': specs,
}
out_json = f'{BASE}/rh10v9pv2w_data.json'
with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f'\n✅ Done!')
print(f'   Gallery  : {len(gallery_out)} images')
print(f'   Features : {len(features_out)} images')
print(f'   Specs    : {len(specs)} items')
print(f'   Saved    : {out_json}')
