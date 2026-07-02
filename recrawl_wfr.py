"""Re-crawl WFR1114WH in strict LG.com PDP order, preserving ALL image variants.

- No dedup: every DZ/D/S/MZ/gallery/feature variant kept
- HTML document order preserved (= PDP display order)
- Original dimensions extracted from binary headers
"""
import re, json, os, sys, io, urllib.request, concurrent.futures as cf
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
PREFIX = '/content/dam/channel/wcms/sa_en'
URL = 'https://www.lg.com/sa_en/washing-machines/front-load/wfr1114wh/'
CODE = 'WFR1114WH'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

EXCLUDE = ['/gnb/','/home-page/','/banners-20','/ai-core-tech','/2025-webos/webos-microsite',
           '/common-icon/','/elements/icons-line/','/members-offer','/multishop','/ministry-of',
           '/oled-speaker/gnb','/spring-sale','/next-day','/watch-it-promo','/av-wm-pto',
           '/bundles-jan','/buy-one-get','/alrajhi','/gnb-banner','/common/common-icon']

# Fetch fresh
path = f'{BASE}/deep_html/WFR1114WH.html'
req = urllib.request.Request(URL, headers={'User-Agent':UA})
with urllib.request.urlopen(req, timeout=30) as r:
    data = r.read()
with open(path,'wb') as f: f.write(data)
print(f'Fetched {len(data):,} bytes')

with open(path,'r',encoding='utf-8',errors='replace') as f:
    html = f.read()

def clean(s):
    s = re.sub(r'<[^>]+>','', s or '')
    s = (s.replace('&#x27;',"'").replace('&amp;','&').replace('&quot;','"')
         .replace('&lt;','<').replace('&gt;','>').replace('&nbsp;',' ')
         .replace('\u201c','"').replace('\u201d','"')
         .replace('\u2018',"'").replace('\u2019',"'"))
    return re.sub(r'\s+',' ', s).strip()

# === Step 1: Extract images in strict DOCUMENT order ===
img_pattern = re.compile(r'/content/dam/channel/wcms/sa_en/[^"\' )]+?\.(?:jpg|jpeg|png|webp)', re.IGNORECASE)
ordered_raw = []  # list of (position_in_html, image_path) in doc order
seen_keep_first = {}  # path -> first position (for "first occurrence" dedup option)

for m in img_pattern.finditer(html):
    ipath = m.group()
    if '/renditions/' in ipath or '/jcr:content/' in ipath: continue
    if any(x in ipath.lower() for x in EXCLUDE): continue
    pos = m.start()
    ordered_raw.append((pos, ipath))
    if ipath not in seen_keep_first:
        seen_keep_first[ipath] = pos

# Identify product-specific folders (same as before)
from collections import Counter
folder_cnt = Counter()
for _, p in ordered_raw:
    parts = p.rstrip('/').split('/')
    if len(parts) >= 4:
        folder_cnt['/'.join(parts[:-1])] += 1
code_l = CODE.lower()
product_folders = set()
for folder, n in folder_cnt.items():
    fl = folder.lower()
    if code_l in fl:
        product_folders.add(folder)
    elif n >= 6 and any(seg in fl for seg in
        ['/features/','/gallery/','/wm/','/washing-machines/']):
        product_folders.add(folder)
for _, p in ordered_raw:
    if code_l in p.lower():
        parts = p.rstrip('/').split('/')
        if len(parts) >= 4:
            product_folders.add('/'.join(parts[:-1]))

# Filter to product-relevant, preserving ORDER + first occurrence only
seen_path = set()
ordered = []
for pos, p in ordered_raw:
    folder = '/'.join(p.rstrip('/').split('/')[:-1])
    if folder not in product_folders: continue
    if p in seen_path: continue
    seen_path.add(p)
    ordered.append((pos, p))

print(f'\nTotal product-relevant images in PDP order: {len(ordered)}')

# Image dimensions via binary headers
def image_dims(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent':UA,'Range':'bytes=0-65536'})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = r.read()
        if data[:2] == b'\xff\xd8':
            i = 2
            while i < len(data)-8:
                if data[i] != 0xFF: break
                marker = data[i+1]
                if 0xC0 <= marker <= 0xCF and marker not in (0xC4,0xC8,0xCC):
                    h = (data[i+5]<<8) | data[i+6]
                    w = (data[i+7]<<8) | data[i+8]
                    return (w, h)
                seglen = (data[i+2]<<8) | data[i+3]
                i += 2 + seglen
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            w = int.from_bytes(data[16:20],'big')
            h = int.from_bytes(data[20:24],'big')
            return (w, h)
        if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            if b'VP8 ' in data[:40]:
                idx = data.index(b'VP8 ')
                w = int.from_bytes(data[idx+14:idx+16],'little') & 0x3FFF
                h = int.from_bytes(data[idx+16:idx+18],'little') & 0x3FFF
                return (w, h)
    except: pass
    return (0, 0)

print('Fetching dimensions for all images...')
dims = {}
def job(pi):
    pos, p = pi
    w, h = image_dims('https://www.lg.com' + p)
    return (p, w, h)
with cf.ThreadPoolExecutor(max_workers=16) as ex:
    for p, w, h in ex.map(job, ordered):
        dims[p] = (w, h)

# === Step 2: Classify each image (gallery vs feature) WITHOUT dedup ===
def classify(p):
    pl = p.lower()
    nm = p.split('/')[-1].lower()
    if 'feature' in pl or '/features/' in pl: return 'feat'
    if '/gallery/' in pl or '-gallery-' in pl: return 'gal'
    if re.match(r'^(d|dz|mz|s|z|l)[-_]?\d+\.', nm): return 'gal'
    if re.match(r'^\d{3}[\._]', nm): return 'gal'
    if 'basic' in nm or 'thumbnail' in nm: return 'gal'
    return 'other'

# === Step 3: Extract title/desc for feature images using HTML proximity ===
def feat_meta(fp, html):
    nm = fp.split('/')[-1]
    idx = html.find(nm)
    if idx < 0: return ('', '')
    snip = html[max(0,idx-2800):idx+2800]
    hs = re.findall(r'<h[23456][^>]*>([\s\S]{1,250}?)</h[23456]>', snip)
    titles = []
    for h in hs:
        t = clean(h)
        if 5 < len(t) < 150 and 'Cookie' not in t and 'Share' not in t:
            titles.append(t)
    ps = re.findall(r'<p[^>]*>([\s\S]{30,900}?)</p>', snip)
    descs = []
    for p in ps:
        t = clean(p)
        if 25 < len(t) < 500 and not any(x in t.lower() for x in
            ['cookie','share this','cartmodel','you can share','absolutely necessary','functional cookies']):
            descs.append(t)
    title = titles[0] if titles else ''
    body = ''
    descs2 = [d for d in descs if d != title and not d.startswith('*')]
    if descs2:
        descs2.sort(key=len)
        body = descs2[0]
    elif descs:
        body = descs[0]
    return (title, body)

# Build gallery and feature lists preserving order
gallery = []
features = []
for pos, p in ordered:
    klass = classify(p)
    w, h = dims.get(p, (0, 0))
    rel = p[len(PREFIX):] if p.startswith(PREFIX) else p
    nm = p.split('/')[-1]
    if klass == 'gal':
        # Derive label from filename
        n = nm.lower()
        if 'basic-large' in n: label='Basic Large'
        elif 'basic' in n: label='Basic'
        elif re.match(r'^dz[-_]?\d', n):
            num = re.match(r'^dz[-_]?(\d+)', n).group(1)
            label=f'DZ-{int(num):02d}'
        elif re.match(r'^d[-_]?\d', n):
            num = re.match(r'^d[-_]?(\d+)', n).group(1)
            label=f'D-{int(num):02d}'
        elif re.match(r'^s[-_]?\d', n):
            num = re.match(r'^s[-_]?(\d+)', n).group(1)
            label=f'S-{int(num):02d}'
        elif re.match(r'^mz[-_]?\d', n):
            num = re.match(r'^mz[-_]?(\d+)', n).group(1)
            label=f'MZ-{int(num):02d}'
        elif re.match(r'^z[-_]?\d', n):
            num = re.match(r'^z[-_]?(\d+)', n).group(1)
            label=f'Z-{int(num):02d}'
        elif 'thumbnail' in n: label='Thumb'
        elif '450' in n: label='450'
        else:
            m = re.search(r'(\d+)', n)
            label = f'View {int(m.group(1)):02d}' if m else nm
        gallery.append({'a':label,'p':rel,'w':w,'h':h,'pos':pos,'file':nm})
    elif klass == 'feat':
        title, body = feat_meta(p, html)
        base = nm.rsplit('.',1)[0]
        am = re.search(r'feature[-_]?(\d+[-_]?\d*[-_]?[a-z0-9\-]*?)(?:[-_]d|[-_]desktop|$)', base, re.I)
        alt = (am.group(1) if am else base[:30]).replace('-',' ').replace('_',' ').strip().title()[:25] or 'Feature'
        features.append({'a':alt,'p':rel,'t':title or alt,'d':body or title or '','w':w,'h':h,'pos':pos,'file':nm})

# Stable sort already (ordered by pos)
print(f'\nGallery: {len(gallery)} items (in PDP HTML order)')
for g in gallery[:20]:
    print(f'  {g["a"]:12s} {g["w"]:4d}x{g["h"]:4d} {g["file"][:55]}')
if len(gallery) > 20: print(f'  ... +{len(gallery)-20} more')

print(f'\nFeatures: {len(features)} items (in PDP HTML order)')
for f in features:
    print(f'  {f["w"]:4d}x{f["h"]:4d}  t="{f["t"][:50]}"  file={f["file"][:50]}')

# === Step 4: JSON-LD product data ===
name, price, msrp = CODE, '', ''
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

# Specs
pairs = re.findall(r'c-compare-selling__spec-name"><p>([\s\S]*?)</p></div><div class="cmp-text c-compare-selling__spec-desc"><p>([\s\S]*?)</p>', html)
specs = {}
for k,v in pairs:
    k = clean(k).rstrip(':').rstrip('\t').strip()
    v = clean(v)
    if k and v and k not in specs:
        specs[k[:40]] = v[:200]

out = {
    'code': CODE, 'name': clean(name), 'price': price, 'msrp': msrp,
    'url': URL,
    'gallery': gallery, 'features': features, 'specs': specs,
}
with open(f'{BASE}/wfr_ordered.json','w',encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f'\nSaved wfr_ordered.json — {len(gallery)} gallery + {len(features)} feat + {len(specs)} specs')
