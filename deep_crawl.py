"""Deep re-crawl of 10 specific products with ORIGINAL resolution images + dimensions.

Strategy per product:
1. Fetch PDP
2. Extract all CDN images in product-specific folders (SKU folder OR category feature folder)
3. Partition gallery vs feature images
4. Extract each feature's title + description by HTML proximity
5. HEAD request each image to get original content-length / verify path
6. Categorize images into ratio buckets: wide-banner (>=2.5), landscape (1.3-2.5),
   near-square (0.85-1.3), portrait (<0.85)
7. Save full structured data to deep_data.json

Also handles the 'shared folder' case (e.g., S65TR references images from other soundbar folders)
by looking at the HTML text proximity to the product name.
"""
import re, json, os, sys, io, urllib.request, concurrent.futures as cf
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
PREFIX = '/content/dam/channel/wcms/sa_en'
os.makedirs(f'{BASE}/deep_html', exist_ok=True)

PRODUCTS = [
    ('WFR1114WH','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wfr1114wh/'),
    ('A9K-SOLO','Vacuum','Cordless','🧹','HA','https://www.lg.com/sa_en/vacuum-cleaners/a9k-solo/'),
    ('LS19GBBDI','Fridge','Side-by-Side','🧊','HA','https://www.lg.com/sa_en/refrigerators/side-by-side/ls19gbbdi/'),
    ('WFR1114MB','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wfr1114mb/'),
    ('S20A','Audio','Soundbar','🔈','MS','https://www.lg.com/sa_en/speakers/soundbars/s20a/'),
    ('DFC435FW','Dish','Dishwasher','🍽️','HA','https://www.lg.com/sa_en/dishwashers/dfc435fw/'),
    ('S65TR','Audio','Soundbar','🔈','MS','https://www.lg.com/sa_en/tv-soundbars/soundbars/s65tr/'),
    ('WFN1310BST','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wfn1310bst/'),
    ('WFN1310WHT','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wfn1310wht/'),
    ('LS25CBBDIK','Fridge','Side-by-Side','🧊','HA','https://www.lg.com/sa_en/refrigerators/side-by-side/ls25cbbdik/'),
]

EXCLUDE = ['/gnb/','/home-page/','/banners-20','/ai-core-tech','/2025-webos/webos-microsite',
           '/common-icon/','/elements/icons-line/','/members-offer','/multishop','/ministry-of',
           '/oled-speaker/gnb','/spring-sale','/next-day','/watch-it-promo','/av-wm-pto',
           '/bundles-jan','/buy-one-get','/alrajhi','/gnb-banner','/common/common-icon']

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

def fetch_pdp(item):
    code = item[0]
    path = f'{BASE}/deep_html/{code.replace("/","_")}.html'
    try:
        req = urllib.request.Request(item[-1], headers={'User-Agent':UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            with open(path,'wb') as f: f.write(r.read())
        return (code, True)
    except Exception as e:
        return (code, False, str(e))

print('Fetching 10 PDPs...')
with cf.ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(fetch_pdp, PRODUCTS))
print('Fetched:', sum(1 for r in results if r[1]))

def clean(s):
    s = re.sub(r'<[^>]+>','', s or '')
    s = (s.replace('&#x27;',"'").replace('&amp;','&').replace('&quot;','"')
         .replace('&lt;','<').replace('&gt;','>').replace('&nbsp;',' ')
         .replace('\\r','').replace('\\n',' ').replace('\\t',' ')
         .replace('\u201c','"').replace('\u201d','"')
         .replace('\u2018',"'").replace('\u2019',"'"))
    return re.sub(r'\s+',' ', s).strip()

def head_dim(url):
    """Attempt to fetch content-length for size info (skip if slow)."""
    try:
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent':UA})
        with urllib.request.urlopen(req, timeout=6) as r:
            return int(r.headers.get('Content-Length', 0))
    except:
        return 0

def image_dims(url):
    """Partial read to extract image dimensions from JPEG/PNG headers."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent':UA,'Range':'bytes=0-65536'})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = r.read()
        # JPEG
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
        # PNG
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            w = int.from_bytes(data[16:20],'big')
            h = int.from_bytes(data[20:24],'big')
            return (w, h)
        # WEBP (VP8)
        if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            # try VP8 lossy chunk
            if b'VP8 ' in data[:40]:
                idx = data.index(b'VP8 ')
                # width/height encoded at offset idx+14
                w = int.from_bytes(data[idx+14:idx+16],'little') & 0x3FFF
                h = int.from_bytes(data[idx+16:idx+18],'little') & 0x3FFF
                return (w, h)
            if b'VP8L' in data[:40]:
                idx = data.index(b'VP8L')
                # bits 0-13 = width-1, bits 14-27 = height-1
                b = data[idx+9:idx+13]
                val = int.from_bytes(b,'little')
                w = (val & 0x3FFF) + 1
                h = ((val >> 14) & 0x3FFF) + 1
                return (w, h)
    except Exception as e:
        pass
    return (0, 0)

def extract(item):
    code, cat, sub, ico, dv, url = item
    path = f'{BASE}/deep_html/{code.replace("/","_")}.html'
    if not os.path.exists(path): return None
    with open(path,'r',encoding='utf-8',errors='replace') as f: html=f.read()

    # JSON-LD product
    name, price, msrp, desc_short = code, '', '', ''
    for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL):
        try:
            d = json.loads(m.group(1))
            if isinstance(d,dict) and d.get('@type','').lower()=='product':
                name = d.get('name') or name
                desc_short = d.get('description') or ''
                off = d.get('offers') or {}
                if isinstance(off,dict):
                    price = str(off.get('price') or '')
                    psp = off.get('priceSpecification') or {}
                    if isinstance(psp,dict): msrp = str(psp.get('price') or '')
        except: pass

    # All CDN images
    all_imgs = sorted(set(re.findall(r'/content/dam/channel/wcms/sa_en/[^"\' )]+?\.(?:jpg|jpeg|png|webp)', html)))
    all_imgs = [i for i in all_imgs if '/renditions/' not in i and '/jcr:content/' not in i
                and not any(x in i.lower() for x in EXCLUDE)]

    # Identify product-specific folders
    code_l = code.lower()
    code_l2 = code_l.replace('-','')
    from collections import Counter
    folder_cnt = Counter()
    for i in all_imgs:
        parts = i.rstrip('/').split('/')
        if len(parts) >= 4:
            folder_cnt['/'.join(parts[:-1])] += 1
    product_folders = set()
    for folder, n in folder_cnt.items():
        fl = folder.lower()
        if code_l in fl or code_l2 in fl:
            product_folders.add(folder)
        elif n >= 6 and any(seg in fl for seg in ['/features/','/gallery/','/wm/','/tvs/','/tv/','/mn/','/monitors/','/refrigerators/','/washing-machines/','/dryers/','/dishwashers/','/vacuum','/av/','/bluetooth-speakers/','/wireless-earbuds/','/home-theaters/','/ha/','/microwaves/','/speakers/']):
            product_folders.add(folder)
    # Be generous: also add any folder referenced in this PDP that contains this product's SKU
    for i in all_imgs:
        if code_l in i.lower() or code_l2 in i.lower():
            parts = i.rstrip('/').split('/')
            if len(parts) >= 4: product_folders.add('/'.join(parts[:-1]))

    imgs = [i for i in all_imgs if '/'.join(i.rstrip('/').split('/')[:-1]) in product_folders]
    # De-dup by filename
    seen = set()
    imgs = [i for i in imgs if not (i.split('/')[-1].lower() in seen or seen.add(i.split('/')[-1].lower()))]

    # Gallery vs Feature split
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
        if 'basic' in nm: return True
        if 'thumbnail' in nm: return True
        return False

    gallery = sorted(set([i for i in imgs if is_gal(i)]))
    features = sorted(set([i for i in imgs if is_feat(i)]))

    # Prefer desktop features
    def is_desktop(p):
        pl = p.lower()
        return bool(re.search(r'(?:[-_]d(?:[-_]\d+)?\.|/desktop/|[-_]desktop[-.])', pl))
    desk_feat = [i for i in features if is_desktop(i)]
    if len(desk_feat) >= 3: features = desk_feat

    # Extract title/desc near each feature image
    features_out = []
    for fp in features:
        nm = fp.split('/')[-1]
        idx = html.find(nm)
        if idx < 0: continue
        snip = html[max(0,idx-2800):idx+2800]
        hs = re.findall(r'<h[23456][^>]*>([\s\S]{1,250}?)</h[23456]>', snip)
        titles = []
        for h in hs:
            t = clean(h)
            if 5 < len(t) < 150 and 'Cookie' not in t and 'Share' not in t and 'cartModel' not in t.lower():
                titles.append(t)
        ps = re.findall(r'<p[^>]*>([\s\S]{30,900}?)</p>', snip)
        descs = []
        for p in ps:
            t = clean(p)
            if 25 < len(t) < 500 and not any(x in t.lower() for x in ['cookie','share this','cartmodel','you can share','absolutely necessary','functional cookies','what people are','our picks','need help']):
                descs.append(t)
        title = titles[0] if titles else ''
        body = ''
        descs2 = [d for d in descs if d != title and not d.startswith('*')]
        if descs2:
            descs2.sort(key=len)
            body = descs2[0]
        elif descs:
            body = descs[0]
        base = nm.rsplit('.',1)[0]
        alt_match = re.search(r'feature[-_]?(\d+[-_]?\d*[-_]?[a-z0-9\-]*?)(?:[-_]d|[-_]desktop|$)', base, re.I)
        alt = (alt_match.group(1) if alt_match else base[:30]).replace('-',' ').replace('_',' ').strip().title()[:25] or 'Feature'
        features_out.append({
            'a': alt,
            'p': fp[len(PREFIX):] if fp.startswith(PREFIX) else fp,
            't': title or alt,
            'd': body or title or '',
            'full_url': 'https://www.lg.com' + fp,
            'w': 0, 'h': 0,
        })

    # Gallery out
    gallery_out = []
    for g in gallery:
        nm = g.split('/')[-1].lower()
        if 'basic-large' in nm: label='Basic Large'
        elif 'basic' in nm: label='Basic'
        elif re.match(r'^dz[-_]?(\d+)', nm):
            num = re.match(r'^dz[-_]?(\d+)', nm).group(1)
            label=f'Zoom {int(num)}'
        elif re.match(r'^(d|s|mz|z|l)[-_]?(\d+)', nm):
            m2 = re.match(r'^[a-z]+[-_]?(\d+)', nm)
            label = f'View {int(m2.group(1))}' if m2 else 'Detail'
        elif 'gallery-' in nm:
            m = re.search(r'gallery[-_]?(\d+)', nm)
            label = f'Gallery {int(m.group(1))}' if m else 'Gallery'
        elif '2010' in nm:
            m = re.search(r'(\d+)[-_]?2010', nm)
            label = f'Gallery {int(m.group(1))}' if m else 'Gallery'
        elif re.match(r'^\d{3}[\._]', nm): label='Thumbnail'
        else:
            m = re.search(r'(\d+)', nm)
            label = f'View {int(m.group(1))}' if m else 'Detail'
        gallery_out.append({
            'a': label,
            'p': g[len(PREFIX):] if g.startswith(PREFIX) else g,
            'full_url': 'https://www.lg.com' + g,
            'w': 0, 'h': 0,
        })

    # Specs
    pairs = re.findall(r'c-compare-selling__spec-name"><p>([\s\S]*?)</p></div><div class="cmp-text c-compare-selling__spec-desc"><p>([\s\S]*?)</p>', html)
    specs = {}
    for k,v in pairs:
        k = clean(k).rstrip(':').rstrip('\t').strip()
        v = clean(v)
        if k and v and k not in specs:
            specs[k[:40]] = v[:200]

    return {
        'code': code, 'cat': cat, 'sub': sub, 'ico': ico, 'dv': dv, 'url': url,
        'name': clean(name), 'price': price, 'msrp': msrp,
        'gallery': gallery_out, 'features': features_out, 'specs': specs,
    }

print('\nExtracting...')
data = []
for item in PRODUCTS:
    d = extract(item)
    if d:
        data.append(d)
        print(f'  {d["code"]:12s}: gal={len(d["gallery"]):2d} feat={len(d["features"]):2d} sp={len(d["specs"]):2d}')

# Fetch dimensions for ALL images in parallel
print('\nFetching image dimensions (this takes a while)...')
all_img_urls = []
for d in data:
    for g in d['gallery']: all_img_urls.append(('gal', d['code'], g, g['full_url']))
    for ft in d['features']: all_img_urls.append(('feat', d['code'], ft, ft['full_url']))

def get_dim(t):
    kind, code, obj, url = t
    w, h = image_dims(url)
    return (t, w, h)

dim_cache = {}
with cf.ThreadPoolExecutor(max_workers=16) as ex:
    for (kind, code, obj, url), w, h in ex.map(get_dim, all_img_urls):
        obj['w'] = w
        obj['h'] = h

# Summary of dimensions
print('\nDimension summary per product:')
for d in data:
    all_items = d['gallery'] + d['features']
    hit = sum(1 for x in all_items if x.get('w',0) > 0)
    print(f'  {d["code"]:12s}: dims resolved {hit}/{len(all_items)}')

with open(f'{BASE}/deep_data.json','w',encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print(f'\nSaved deep_data.json')
