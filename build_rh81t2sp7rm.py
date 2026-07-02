"""Crawl RH81T2SP7RM dryer from LG Saudi Arabia."""
import urllib.request, re, json, sys, io, struct, concurrent.futures as cf
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120'
CDN = 'https://www.lg.com/content/dam/channel/wcms/sa_en'
BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
CODE = 'RH81T2SP7RM'
URL  = 'https://www.lg.com/sa_en/dryers/rh81t2sp7rm/'

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode('utf-8', errors='replace')

def get_dims(path):
    try:
        url = ('https://www.lg.com' + path) if path.startswith('/content') else (CDN + path)
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

def get_alt(txt, filename):
    idx = txt.find(filename)
    if idx < 0: return ''
    chunk = txt[idx:idx+600]
    m = re.search(r'imageAltText[^:]*:\s*"([^"]{5,})"', chunk)
    return m.group(1).strip() if m else ''

print(f'Fetching {CODE}...')
html = fetch(URL)
chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
combined = ''.join(chunks).replace('\\n','\n').replace('\\"','"').replace('\\\\','\\')
print(f'Page: {len(html):,}, next_f: {len(combined):,}')

# Price
price_m = re.search(r'"price":"([0-9.]+)"', html)
price = float(price_m.group(1)) if price_m else 0
msrp_m = re.search(r'originalPrice[^0-9]*([0-9,]+(?:\.[0-9]+)?)', combined)
msrp = float(msrp_m.group(1).replace(',','')) if msrp_m else None
print(f'Price: {price}, MSRP: {msrp}')

# Name
name_m = re.search(r'"name"\s*:\s*"(LG[^"]{5,80})"', html)
name = name_m.group(1) if name_m else f'LG Dryer {CODE}'
print(f'Name: {name}')

# All product image paths
code_lower = CODE.lower()
all_paths_raw = re.findall(r'(/(?:images|content/dam)[^"\\<>\s]+\.(?:jpg|png|webp))', combined)
seen_p = set()
unique = []
for p in all_paths_raw:
    base = p.split('/jcr:')[0].split('?')[0]
    rel = re.sub(r'.*/wcms/sa_en', '', base)
    if not rel: rel = base
    if re.search(r'gnb|banner|home-page|logo|favicon|spring|multishop|ministry|icon', rel, re.I): continue
    if code_lower not in rel.lower() and 'rh81' not in rel.lower(): continue
    if rel not in seen_p:
        seen_p.add(rel)
        unique.append(rel)

print(f'Found {len(unique)} product images:')
for p in sorted(unique): print(f'  {p}')

# Classify: gallery = DZ or gallery in name; feature = others
gallery_paths = [p for p in unique if re.search(r'DZ-\d+|gallery', p, re.I) and 'thumbnail' not in p.lower() and 'mobilezoom' not in p.lower() and '-S-' not in p]
feat_paths    = [p for p in unique if p not in gallery_paths and re.search(r'feature|D\d{2}|desktop|-d\.jpg|-d-\d', p, re.I) and 'mobile' not in p.lower() and '-m-' not in p.lower() and '-m.' not in p.lower()]

print(f'\nGallery ({len(gallery_paths)}): {[p.split("/")[-1] for p in gallery_paths]}')
print(f'Features ({len(feat_paths)}): {[p.split("/")[-1] for p in feat_paths]}')

gallery = []
for p in gallery_paths[:16]:
    fn = p.split('/')[-1]
    alt = get_alt(combined, fn) or f'LG Dryer {CODE}'
    gallery.append({'a': alt, 'p': p})

features = []
for p in feat_paths[:16]:
    fn = p.split('/')[-1]
    alt = get_alt(combined, fn)
    # Derive title from filename
    t = re.sub(r'^.*?d\d+-\d+-?', '', fn, flags=re.I)
    t = re.sub(r'-d(-\d+)?(-v\d+)?\.jpg$', '', t)
    t = re.sub(r'-d\.jpg$', '', t)
    t = t.replace('-', ' ').strip().title()
    if not t or len(t) < 3:
        t = fn.replace('.jpg','').replace('-d','').replace('-',' ').title()
    # Try get description from page text
    d = ''
    idx = combined.find(t[:15])
    if idx >= 0:
        ctx_lines = combined[idx:idx+400].split('\n')
        for line in ctx_lines:
            l = line.strip()
            if 20 < len(l) < 200 and not l.startswith('{') and not l.startswith('"image'):
                d = l; break
    features.append({'a': alt or t, 'p': p, 't': t, 'd': d})

# Fetch dims
print('\nFetching dimensions...')
all_imgs = gallery + features
def fetch_dim(item):
    w, h = get_dims(item['p'])
    return item, w, h
with cf.ThreadPoolExecutor(max_workers=10) as ex:
    for item, w, h in ex.map(fetch_dim, all_imgs):
        if w and h: item['w'] = w; item['h'] = h
        print(f'  {item["p"].split("/")[-1][:55]:55s} {item.get("w","?")}x{item.get("h","?")}')

# Specs
specs = {}
spec_keys = ['Motor','Capacity','Energy','Noise','Color','Dimension','Weight','Program','Temperature','Time','Sensor']
for k in spec_keys:
    idx = combined.find(k)
    if idx >= 0:
        ctx = combined[idx:idx+150].replace('\n',' ')
        m = re.search(k + r'[^:]*:\s*([^\n"]{3,60})', ctx)
        if m: specs[k] = m.group(1).strip()

product = {
    'code': CODE, 'name': name, 'price': price, 'msrp': msrp,
    'url': URL, 'cat': 'Dryer', 'sub': 'Heat Pump', 'ico': 'dryer', 'dv': 'HA',
    'gallery': gallery, 'features': features, 'specs': specs,
}
print(f'\nSummary: gal={len(gallery)}, feat={len(features)}, specs={len(specs)}')
with open(f'{BASE}/rh81t2sp7rm_data.json', 'w', encoding='utf-8') as f:
    json.dump(product, f, ensure_ascii=False, indent=2)
print(f'Saved rh81t2sp7rm_data.json')
