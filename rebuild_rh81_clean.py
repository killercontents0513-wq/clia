"""Clean rebuild of RH81T2SP7RM from saved HTML + live dims."""
import re, json, sys, io, urllib.request, struct, concurrent.futures as cf
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
CDN  = 'https://www.lg.com/content/dam/channel/wcms/sa_en'
UA   = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120'
CODE = 'RH81T2SP7RM'

# ── Load saved HTML ──────────────────────────────────────────────────────────
with open(f'{BASE}/bulk_html/{CODE}.html','r',encoding='utf-8',errors='replace') as f:
    html = f.read()
print(f'HTML: {len(html):,} bytes')

# ── Get alt texts from next_f data ───────────────────────────────────────────
chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
nf = ''.join(chunks).replace('\\n','\n').replace('\\"','"').replace('\\\\','\\')

def get_alt(txt, fn):
    idx = txt.find(fn)
    if idx < 0: return ''
    chunk = txt[idx:idx+600]
    m = re.search(r'imageAltText[^:]*:\s*"([^"]{5,})"', chunk)
    return m.group(1).strip() if m else ''

def clean_html(s):
    s = re.sub(r'<[^>]+>','',s or '')
    return re.sub(r'\s+',' ',s.replace('&amp;','&').replace('&quot;','"').replace('&#x27;',"'").replace('&nbsp;',' ')).strip()

# ── Name / Price from JSON-LD ────────────────────────────────────────────────
name, price, msrp = CODE, 0, None
for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL):
    try:
        d = json.loads(m.group(1))
        if isinstance(d,dict) and d.get('@type','').lower()=='product':
            name = d.get('name') or name
            off  = d.get('offers') or {}
            if isinstance(off,dict):
                price = float(off.get('price') or 0)
                psp   = off.get('priceSpecification') or {}
                if isinstance(psp,dict) and psp.get('price'):
                    msrp = float(psp['price'])
    except: pass
print(f'Name : {name}')
print(f'Price: {price}  MSRP: {msrp}')

# ── Dimensions fetcher ───────────────────────────────────────────────────────
def get_dims(path):
    try:
        url = ('https://www.lg.com'+path) if path.startswith('/content') else (CDN+path)
        req = urllib.request.Request(url, headers={'User-Agent':UA,'Range':'bytes=0-65535'})
        with urllib.request.urlopen(req, timeout=10) as r: data = r.read()
        if data[:2] == b'\xff\xd8':
            i=2
            while i<len(data)-8:
                if data[i]!=0xff: break
                mk=data[i+1]
                if mk in (0xc0,0xc1,0xc2):
                    return struct.unpack('>H',data[i+7:i+9])[0], struct.unpack('>H',data[i+5:i+7])[0]
                i+=2+struct.unpack('>H',data[i+2:i+4])[0]
        if data[:8]==b'\x89PNG\r\n\x1a\n':
            return struct.unpack('>I',data[16:20])[0], struct.unpack('>I',data[20:24])[0]
    except: pass
    return 0,0

# ── Gallery: DZ-01 → DZ-15 in exact order ───────────────────────────────────
gallery = []
for i in range(1,16):
    fn  = f'DZ-{str(i).zfill(2)}.jpg'
    alt = get_alt(nf, fn) or get_alt(html, fn) or f'LG Dryer {CODE} view {i}'
    gallery.append({'a':alt, 'p':f'/images/dryers/{CODE}/{fn}'})
print(f'Gallery: {len(gallery)} images (DZ-01 → DZ-15)')

# ── Features: desktop only, from /wm/features/, sorted ──────────────────────
FEAT_FILES = [
    ('dryer-vestel-odm-dryer-white-01-intro-d.jpg',         '', ''),
    ('dryer-vestel-odm-dryer-white-02-2-1-heater-dryer-d.jpg','Enjoy the Gentle Dry with Heat Pump','Heat Pump Dries laundry at low temperatures, gentle on clothes.'),
    ('dryer-vestel-odm-dryer-white-02-2-2-heatpump-dryer-d.jpg','Heat Pump Dryer vs Heater Dryer','With Heat Pump technology, drying is more energy-efficient and gentler on your clothes.'),
    ('dryer-vestel-odm-dryer-white-05-2-1-washer-and-dryer-d.jpg','Visible and Elegant Design','Stylish design fits seamlessly into modern home interiors.'),
    ('dryer-vestel-odm-dryer-white-05-2-2-door-d.jpg',      'Easy-Open Door','Large door opening makes loading and unloading effortless.'),
    ('dryer-vestel-odm-dryer-white-05-2-3-control-panel-d.jpg','Intuitive Control Panel','Clear LCD display and simple controls for easy operation.'),
]
FEAT_BASE = '/images/wm/features/'

features = []
for fn, default_t, default_d in FEAT_FILES:
    path = FEAT_BASE + fn
    # Try to get title/desc from page HTML near this filename
    idx = html.find(fn)
    t, d = default_t, default_d
    if idx >= 0:
        snip = html[max(0,idx-2500):idx+2500]
        hs = re.findall(r'<h[23456][^>]*>([\s\S]{1,250}?)</h[23456]>',snip)
        for h in hs:
            ct = clean_html(h)
            if ct and 5<len(ct)<120 and 'Cookie' not in ct:
                t = ct; break
        ps = re.findall(r'<p[^>]*>([\s\S]{30,500}?)</p>',snip)
        for p in ps:
            cp = clean_html(p)
            if 25<len(cp)<300 and not any(x in cp.lower() for x in ['cookie','share','cartmodel','absolutely necessary']):
                if cp != t: d = cp; break
    alt = get_alt(nf, fn) or t
    features.append({'a':alt,'p':path,'t':t or fn.replace('-d.jpg','').replace('-',' ').title(),'d':d})

print(f'Features: {len(features)} images')

# ── Fetch all dimensions concurrently ────────────────────────────────────────
print('Fetching dimensions...')
all_items = gallery + features
def fetch_dim(item):
    w,h = get_dims(item['p'])
    return item,w,h
with cf.ThreadPoolExecutor(max_workers=12) as ex:
    for item,w,h in ex.map(fetch_dim,all_items):
        if w and h: item['w']=w; item['h']=h
        print(f'  {item["p"].split("/")[-1]:55s} {item.get("w","?")}x{item.get("h","?")}')

# ── Specs from HTML comparison table ────────────────────────────────────────
pairs = re.findall(r'c-compare-selling__spec-name"><p>([\s\S]*?)</p></div><div class="cmp-text c-compare-selling__spec-desc"><p>([\s\S]*?)</p>',html)
specs = {}
for k,v in pairs:
    k=clean_html(k).rstrip(':').strip(); v=clean_html(v)
    if k and v and k not in specs: specs[k[:40]]=v[:200]
    if len(specs)>=25: break

# ── Build product entry ──────────────────────────────────────────────────────
product = {
    'code':CODE,'cat':'Dryer','sub':'Heat Pump','ico':'dryer','dv':'HA',
    'url':'https://www.lg.com/sa_en/dryers/rh81t2sp7rm/',
    'name':name,'price':price,'msrp':msrp,
    'gallery':gallery,'features':features,'specs':specs,
}
print(f'\nFinal: gal={len(gallery)}, feat={len(features)}, specs={len(specs)}')

# ── Update bulk_data.json ────────────────────────────────────────────────────
with open(f'{BASE}/bulk_data.json','r',encoding='utf-8') as f:
    bulk = json.load(f)
bulk = [product if p['code']==CODE else p for p in bulk]
with open(f'{BASE}/bulk_data.json','w',encoding='utf-8') as f:
    json.dump(bulk,f,ensure_ascii=False,indent=1)
print('bulk_data.json updated.')

# ── Gallery order check ──────────────────────────────────────────────────────
print('\nGallery order:')
for g in gallery:
    print(f'  {g["p"].split("/")[-1]:15s} {g.get("w","?")}x{g.get("h","?")}  {g["a"]}')
print('\nFeatures:')
for ft in features:
    print(f'  [{ft.get("w","?")}x{ft.get("h","?")}] {ft["t"][:50]:50s}')
