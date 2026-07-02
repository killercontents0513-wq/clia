"""Fix and integrate RH81T2SP7RM and A9LSLIM into bulk_data.json."""
import urllib.request, re, json, sys, io, struct, concurrent.futures as cf
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120'
CDN = 'https://www.lg.com/content/dam/channel/wcms/sa_en'
BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'

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

def fetch_page_data(url):
    html = fetch(url)
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
    combined = ''.join(chunks).replace('\\n','\n').replace('\\"','"').replace('\\\\','\\')
    price_m = re.search(r'"price":"([0-9.]+)"', html)
    price = float(price_m.group(1)) if price_m else 0
    name_m = re.search(r'"name"\s*:\s*"(LG[^"]{5,80})"', html)
    name = name_m.group(1) if name_m else ''
    return combined, price, name

# ═══════════════════════════════════════════════════
# RH81T2SP7RM - fix: use MZ as feature images
# ═══════════════════════════════════════════════════
print('=== RH81T2SP7RM ===')
with open(f'{BASE}/rh81t2sp7rm_data.json', 'r', encoding='utf-8') as f:
    rh81 = json.load(f)

combined_rh81, _, _ = fetch_page_data('https://www.lg.com/sa_en/dryers/rh81t2sp7rm/')

# Get proper name
name_m = re.search(r'bulletFeatureDesc[^:]*:\s*"([^"]+)"', combined_rh81)
# Find product name from page text
page_text_rh81 = re.sub(r'<[^>]+>', '', combined_rh81)
# Try schema
name_schema = re.search(r'"name"\s*:\s*"(LG[^"]{10,80}(?:Dryer|dryer|Heat Pump)[^"]{0,40})"', combined_rh81)
if name_schema:
    rh81['name'] = name_schema.group(1)
    print(f'Name: {rh81["name"]}')
else:
    # Search for dryer-related name
    idx = combined_rh81.find('Heat Pump')
    if idx >= 0:
        ctx = combined_rh81[max(0,idx-100):idx+100]
        print(f'Heat Pump ctx: {ctx[:150]}')
    rh81['name'] = 'LG Heat Pump Dryer 8kg'

# Build MZ feature images with alt texts
MZ_PATH = '/images/dryers/RH81T2SP7RM/'
mz_features = []
for i in range(1, 16):
    n = str(i).zfill(2)
    fn = f'MZ-{n}.jpg'
    alt = get_alt(combined_rh81, fn)
    # Try to derive title from alt text
    t = alt[:60] if alt else f'LG Dryer Feature {n}'
    d = ''
    mz_features.append({'a': alt or t, 'p': MZ_PATH + fn, 't': t, 'd': d})
    print(f'  MZ-{n}: {alt[:60]}')

# Fetch dims for MZ
print('Fetching MZ dims...')
def fetch_dim(item):
    w, h = get_dims(item['p'])
    return item, w, h
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for item, w, h in ex.map(fetch_dim, mz_features):
        if w and h: item['w'] = w; item['h'] = h
        print(f'  {item["p"].split("/")[-1]}: {item.get("w","?")}x{item.get("h","?")}')

rh81['features'] = mz_features
print(f'RH81 done: gal={len(rh81["gallery"])}, feat={len(rh81["features"])}')

# ═══════════════════════════════════════════════════
# A9LSLIM - fix: gallery = DZ only, clean features
# ═══════════════════════════════════════════════════
print('\n=== A9LSLIM ===')
with open(f'{BASE}/a9lslim_data.json', 'r', encoding='utf-8') as f:
    a9l = json.load(f)

# Fix gallery: keep only DZ images
a9l['gallery'] = [g for g in a9l['gallery'] if '/DZ-' in g['p']]
print(f'Gallery fixed: {len(a9l["gallery"])} DZ images')

# Fix features: remove duplicates, keep only desktop/SA locale ones
seen_feat = set()
clean_features = []
for ft in a9l['features']:
    fn = ft['p'].split('/')[-1]
    # Skip hk_en sourced duplicates if sa version exists
    if 'hk_en' in ft['p']: continue
    # Skip tiny images
    if ft.get('w',999) < 500 or ft.get('h',999) < 400: continue
    # Skip -t. (tablet) variants
    if re.search(r'-t\.jpg$', fn): continue
    # Skip design-2/3/4 (keep only design-1)
    if re.search(r'design-[234]-d', fn): continue
    # Deduplicate by filename
    if fn in seen_feat: continue
    seen_feat.add(fn)
    # Fix feature title from filename
    t = re.sub(r'^vac-codezero-a9-air-2024-\d+-\d*-?', '', fn)
    t = re.sub(r'-d(-\d+)?\.jpg$', '', t)
    t = t.replace('-', ' ').strip().title()
    if not t or len(t) < 3:
        t = ft.get('t', fn.replace('.jpg',''))
    ft['t'] = t
    if not ft.get('a'): ft['a'] = t
    clean_features.append(ft)
    print(f'  {t[:45]:45s} {fn[:45]:45s} {ft.get("w","?")}x{ft.get("h","?")}')

a9l['features'] = clean_features
print(f'A9LSLIM done: gal={len(a9l["gallery"])}, feat={len(a9l["features"])}')

# ═══════════════════════════════════════════════════
# Integrate into bulk_data.json
# ═══════════════════════════════════════════════════
print('\n=== Integrating ===')
with open(f'{BASE}/bulk_data.json', 'r', encoding='utf-8') as f:
    bulk = json.load(f)

# Remove old entries
bulk = [x for x in bulk if x['code'] not in ('RH81T2SP7RM', 'A9LSLIM')]

# Insert at top in crawl order (A9LSLIM first = most recent)
bulk.insert(0, a9l)
bulk.insert(0, rh81)

with open(f'{BASE}/bulk_data.json', 'w', encoding='utf-8') as f:
    json.dump(bulk, f, ensure_ascii=False, indent=1)

print(f'bulk_data.json: {len(bulk)} products')
print('Top 6:')
for p in bulk[:6]:
    print(f'  {p["code"]:20s} gal={len(p.get("gallery",[]))} feat={len(p.get("features",[]))}')
