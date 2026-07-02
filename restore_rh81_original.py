"""Restore RH81T2SP7RM to original bulk_extract2.py output, then update bulk_data.json."""
import re, json, os, sys, io, urllib.request, struct, concurrent.futures as cf
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
PREFIX = '/content/dam/channel/wcms/sa_en'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120'
CDN = 'https://www.lg.com/content/dam/channel/wcms/sa_en'

EXCLUDE_PATHS = [
    '/gnb/','/home-page/','/banners-20','/ai-core-tech','/2025-webos/webos-microsite',
    '/common-icon/','/elements/icons-line/','/members-offer','/multishop','/ministry-of',
    '/oled-speaker/gnb','/spring-sale','/next-day','/watch-it-promo','/av-wm-pto',
    '/bundles-jan','/buy-one-get','/alrajhi','/gnb-banner'
]

def clean_html(s):
    s = re.sub(r'<[^>]+>','', s or '')
    s = (s.replace('&#x27;',"'").replace('&amp;','&').replace('&quot;','"')
         .replace('&lt;','<').replace('&gt;','>').replace('&nbsp;',' ')
         .replace('\\r','').replace('\\n',' ').replace('\\t',' '))
    return re.sub(r'\s+',' ', s).strip()

def is_excluded(p):
    pl = p.lower()
    return any(x in pl for x in EXCLUDE_PATHS)

def get_dims(path):
    try:
        if path.startswith('/content'):
            url = 'https://www.lg.com' + path
        else:
            url = CDN + path
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Range': 'bytes=0-65535'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
        if data[:2] == b'\xff\xd8':
            i = 2
            while i < len(data)-8:
                if data[i] != 0xff: break
                marker = data[i+1]
                if marker in (0xc0,0xc1,0xc2):
                    h = struct.unpack('>H', data[i+5:i+7])[0]
                    w = struct.unpack('>H', data[i+7:i+9])[0]
                    return w, h
                length = struct.unpack('>H', data[i+2:i+4])[0]
                i += 2 + length
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return struct.unpack('>I', data[16:20])[0], struct.unpack('>I', data[20:24])[0]
    except: pass
    return 0, 0

# ── Read saved HTML ──────────────────────────────────────────────────────────
code = 'RH81T2SP7RM'
path = f'{BASE}/bulk_html/{code}.html'
print(f'Reading {path}...')
with open(path, 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()
print(f'HTML size: {len(html):,}')

# ── JSON-LD for name/price ───────────────────────────────────────────────────
name, price, msrp = code, '', ''
for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL):
    try:
        d = json.loads(m.group(1))
        if isinstance(d,dict) and d.get('@type','').lower()=='product':
            name = d.get('name') or name
            off = d.get('offers') or {}
            if isinstance(off,dict):
                price = str(off.get('price') or '')
                psp = off.get('priceSpecification') or {}
                if isinstance(psp,dict): msrp = str(psp.get('price') or '')
    except: pass
name = (name or code).strip()
print(f'Name: {name}, Price: {price}, MSRP: {msrp}')

# ── All CDN images ───────────────────────────────────────────────────────────
all_imgs = sorted(set(re.findall(r'/content/dam/channel/wcms/sa_en/[^"\' )]+?\.(?:jpg|jpeg|png|webp)', html)))
all_imgs = [i for i in all_imgs if '/renditions/' not in i and '/jcr:content/' not in i and not is_excluded(i)]
print(f'Raw CDN images: {len(all_imgs)}')

code_l = code.lower()
code_nodash = code.lower().replace('-','')
from collections import Counter
folders = Counter()
for i in all_imgs:
    parts = i.rstrip('/').split('/')
    if len(parts) >= 4:
        folder = '/'.join(parts[:-1])
        folders[folder] += 1

product_folders = set()
for folder, n in folders.items():
    fl = folder.lower()
    if code_l in fl or code_nodash in fl:
        product_folders.add(folder)
    elif n >= 8 and ('/images/' in fl) and any(seg in fl for seg in ['/features/','gallery','/wm/','/tvs/','/tv/','/mn/','/monitors/','/refrigerators/','/washing-machines/','/dryers/','/dishwashers/','/vacuum','/av/','/bluetooth-speakers/','/wireless-earbuds/','/home-theaters/','/ha/','/microwaves/']):
        product_folders.add(folder)

for i in all_imgs:
    if code_l in i.lower() or code_nodash in i.lower():
        parts = i.rstrip('/').split('/')
        if len(parts) >= 4:
            product_folders.add('/'.join(parts[:-1]))

print(f'Product folders: {sorted(product_folders)}')

imgs = [i for i in all_imgs if any(pf == '/'.join(i.rstrip('/').split('/')[:-1]) for pf in product_folders)]
seen_fn = set()
imgs = [i for i in imgs if not (i.split('/')[-1].lower() in seen_fn or seen_fn.add(i.split('/')[-1].lower()))]
print(f'Filtered images: {len(imgs)}')
for i in imgs: print(f'  {i}')

# ── Gallery vs Feature ───────────────────────────────────────────────────────
def is_feature(p):
    pl = p.lower()
    return 'feature' in pl or '/features/' in pl

def is_gallery(p):
    pl = p.lower()
    nm = p.split('/')[-1].lower()
    if is_feature(p): return False
    if '/gallery/' in pl or '-gallery-' in pl: return True
    if re.match(r'^(d|dz|mz|s|z|l)[-_]?\d+\.', nm): return True
    if re.match(r'^\d{3}[\._]', nm): return True
    if 'basic' in nm and ('450' in nm or 'large' in nm or nm.endswith('_basic.jpg') or 'basic_' in nm): return True
    if re.match(r'^\d+-\d+\.', nm): return True
    if re.search(r'basic|zoom|thumbnail|hr-images', nm): return True
    return False

gallery_raw = [i for i in imgs if is_gallery(i)]
feature_raw = [i for i in imgs if is_feature(i)]

def is_desktop(p):
    pl = p.lower()
    return bool(re.search(r'(?:[-_]d(?:[-_]\d+)?\.|/desktop/|[-_]desktop[-.])', pl))
def is_mobile(p):
    pl = p.lower()
    return bool(re.search(r'[-_]m(?:obile)?(?:[-_]\d+)?\.|/mobile/|[-_]mobile[-.]', pl))

desktop_feats = [i for i in feature_raw if is_desktop(i)]
if len(desktop_feats) >= 3:
    feat_final = desktop_feats
else:
    feat_final = [i for i in feature_raw if not is_mobile(i)] or feature_raw

def gallery_rank(p):
    nm = p.split('/')[-1].lower()
    if 'basic-large' in nm or 'basic_large' in nm: return 1
    if '2010' in nm: return 2
    if re.match(r'^dz[-_]', nm) or nm.startswith('zoom') or 'zoom' in nm: return 3
    if 'gallery-0' in nm or 'gallery_' in nm: return 4
    if re.match(r'^d[-_]\d+', nm): return 5
    if '450' in nm or 'basic' in nm: return 6
    if re.match(r'^s[-_]', nm): return 8
    if re.match(r'^(mz|m)[-_]', nm): return 9
    if 'thumbnail' in nm: return 9
    return 7

gallery_sorted = sorted(gallery_raw, key=lambda p:(gallery_rank(p), p))

def pos_key(p):
    nm = p.split('/')[-1].lower()
    m = re.search(r'(\d{1,2})(?=\.|[-_])', nm)
    return m.group(1) if m else nm

seen_pos = {}
gallery_final = []
for p in gallery_sorted:
    k = pos_key(p)
    if k not in seen_pos:
        seen_pos[k] = True
        gallery_final.append(p)

gallery_final = gallery_final[:25]
feat_final = feat_final[:25]

def rel(p): return p[len(PREFIX):] if p.startswith(PREFIX) else p

print(f'\nGallery raw: {len(gallery_raw)}, final: {len(gallery_final)}')
for g in gallery_final: print(f'  {g}')
print(f'\nFeatures raw: {len(feature_raw)}, final: {len(feat_final)}')
for f in feat_final: print(f'  {f}')

# ── Extract feature titles/descs ─────────────────────────────────────────────
features_out = []
for fn_full in feat_final:
    nm = fn_full.split('/')[-1]
    idx = html.find(nm)
    if idx < 0: continue
    snip = html[max(0,idx-2500):idx+2500]
    hs = re.findall(r'<h[23456][^>]*>([\s\S]{1,250}?)</h[23456]>', snip)
    titles = []
    for h in hs:
        t = clean_html(h)
        if t and 5 < len(t) < 150 and 'Cookie' not in t and 'Share' not in t and 'cartModel' not in t.lower():
            titles.append(t)
    ps = re.findall(r'<p[^>]*>([\s\S]{30,900}?)</p>', snip)
    descs = []
    for p in ps:
        t = clean_html(p)
        if 25 < len(t) < 400 and not any(x in t.lower() for x in ['cookie','share this','cartmodel','you can share','absolutely necessary','functional cookies','what people are','our picks','need help','our story']):
            descs.append(t)
    title = titles[0] if titles else ''
    desc = ''
    descs2 = [d for d in descs if d != title and not d.startswith('*')]
    if descs2:
        descs2.sort(key=len)
        desc = descs2[0]
    elif descs:
        desc = descs[0]
    base = nm.rsplit('.',1)[0]
    alt_match = re.search(r'feature[-_]?(\d+[-_]?\d*[-_]?[a-z0-9\-]*?)(?:[-_]d|[-_]desktop|$)', base, re.I)
    alt = (alt_match.group(1) if alt_match else base[:30]).replace('-',' ').replace('_',' ').strip().title()[:25] or 'Feature'
    features_out.append({'a':alt,'p':rel(fn_full),'t':title or alt,'d':desc or title or ''})

# ── Gallery labels ────────────────────────────────────────────────────────────
gallery_out = []
for g in gallery_final:
    nm = g.split('/')[-1].lower()
    if 'basic-large' in nm: label='Basic Large'
    elif 'basic' in nm: label='Basic'
    elif re.match(r'^dz[-_]?(\d+)', nm):
        num = re.match(r'^dz[-_]?(\d+)', nm).group(1)
        label=f'Zoom {int(num)}'
    elif re.match(r'^(d|s|mz|z|l)[-_]?(\d+)', nm):
        num = re.match(r'^(?:[a-z])[-_]?(\d+)', nm).group(1)
        label=f'View {int(num)}'
    elif 'gallery-' in nm:
        m2 = re.search(r'gallery[-_]?(\d+)', nm)
        label = f'Gallery {int(m2.group(1))}' if m2 else 'Gallery'
    elif '2010' in nm:
        m2 = re.search(r'(\d+)[-_]?2010', nm)
        label = f'Gallery {int(m2.group(1))}' if m2 else 'Gallery'
    elif re.match(r'^\d{3}[\._]', nm): label='Thumbnail'
    else:
        m2 = re.search(r'(\d+)', nm)
        label = f'View {int(m2.group(1))}' if m2 else 'Detail'
    gallery_out.append({'a':label,'p':rel(g)})

print(f'\nFinal: gal={len(gallery_out)}, feat={len(features_out)}')

# ── Fetch dimensions ──────────────────────────────────────────────────────────
print('\nFetching dimensions...')
all_items = gallery_out + features_out
def fetch_dim(item):
    w, h = get_dims(item['p'])
    return item, w, h
with cf.ThreadPoolExecutor(max_workers=10) as ex:
    for item, w, h in ex.map(fetch_dim, all_items):
        if w and h: item['w'] = w; item['h'] = h
        print(f'  {item["p"].split("/")[-1][:55]:55s} {item.get("w","?")}x{item.get("h","?")}')

# ── Specs from HTML ───────────────────────────────────────────────────────────
pairs = re.findall(r'c-compare-selling__spec-name"><p>([\s\S]*?)</p></div><div class="cmp-text c-compare-selling__spec-desc"><p>([\s\S]*?)</p>', html)
specs = {}
for k,v in pairs:
    k = clean_html(k).rstrip(':').rstrip('\t').strip()
    v = clean_html(v)
    if k and v and k not in specs:
        specs[k[:40]] = v[:200]
    if len(specs) >= 30: break

# ── Build final product ───────────────────────────────────────────────────────
restored = {
    'code': code,
    'cat': 'Dryer', 'sub': 'Heat Pump', 'ico': 'dryer', 'dv': 'HA',
    'url': 'https://www.lg.com/sa_en/dryers/rh81t2sp7rm/',
    'name': name,
    'price': float(price) if price else 0,
    'msrp': float(msrp) if msrp else None,
    'gallery': gallery_out,
    'features': features_out,
    'specs': specs,
}

# ── Patch bulk_data.json ──────────────────────────────────────────────────────
with open(f'{BASE}/bulk_data.json', 'r', encoding='utf-8') as f:
    bulk = json.load(f)

# Keep current price from bulk if restored price is 0
old = next((p for p in bulk if p['code'] == code), None)
if old and old.get('price') and not restored['price']:
    restored['price'] = old['price']
if old and old.get('msrp') and not restored['msrp']:
    restored['msrp'] = old['msrp']

# Replace in place
bulk = [restored if p['code'] == code else p for p in bulk]

with open(f'{BASE}/bulk_data.json', 'w', encoding='utf-8') as f:
    json.dump(bulk, f, ensure_ascii=False, indent=1)

print(f'\nRestored RH81T2SP7RM: gal={len(gallery_out)}, feat={len(features_out)}, specs={len(specs)}')
print('bulk_data.json updated.')

# Show features
print('\nFeatures:')
for ft in features_out:
    print(f'  [{ft.get("w","?")}x{ft.get("h","?")}] {ft["t"][:50]:50s} {ft["p"].split("/")[-1]}')
print('\nGallery (first 5):')
for g in gallery_out[:5]:
    print(f'  [{g.get("w","?")}x{g.get("h","?")}] {g["a"]:15s} {g["p"].split("/")[-1]}')
