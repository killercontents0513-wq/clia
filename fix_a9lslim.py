"""Fix A9LSLIM gallery (DZ-01 to DZ-15) and update bulk_data.json."""
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

print('Fetching A9LSLIM page data...')
html = fetch('https://www.lg.com/sa_en/vacuum-cleaners/a9lslim/')
chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
combined = ''.join(chunks).replace('\\n','\n').replace('\\"','"').replace('\\\\','\\')

GPATH = '/images/vacuum-cleaners/a9lslim-bcbgnag/gallery/'

# Build DZ-01 to DZ-15
gallery = []
for i in range(1, 16):
    n = str(i).zfill(2)
    fn = f'DZ-{n}.jpg'
    alt = get_alt(combined, fn) or f'LG CordZero A9 Slim - view {i}'
    gallery.append({'a': alt, 'p': GPATH + fn})

# Fetch dims
print('Fetching gallery dims...')
def fetch_dim(item):
    w, h = get_dims(item['p'])
    return item, w, h
with cf.ThreadPoolExecutor(max_workers=10) as ex:
    for item, w, h in ex.map(fetch_dim, gallery):
        if w and h: item['w'] = w; item['h'] = h
        print(f'  {item["p"].split("/")[-1]}: {item.get("w","?")}x{item.get("h","?")}')

# Load bulk and update
with open(f'{BASE}/bulk_data.json', 'r', encoding='utf-8') as f:
    bulk = json.load(f)

a9l = next(p for p in bulk if p['code'] == 'A9LSLIM')
a9l['gallery'] = gallery
print(f'\nA9LSLIM gallery updated: {len(gallery)} images')

# Also fix feature titles
feat_title_map = {
    'intro': ('LG CordZero A9 Slim', 'The CordZero A9 Slim combines powerful suction with an ultra-slim design for effortless whole-home cleaning.'),
    'lightweight-yet-powerful': ('Lightweight Yet Powerful', 'At just 1.43kg, the A9 Slim delivers powerful suction without the fatigue of heavier vacuums.'),
    'a9_generated': ('AI-Generated Insights', 'Smart cleaning technology provides intelligent recommendations to optimize your cleaning routine.'),
    'dual-turbo-cyclone': ('Dual Turbo Cyclone', 'The dual turbo cyclone system maintains powerful suction by preventing fine dust from clogging the filter.'),
    'slim-design': ('Ultra-Slim Design', 'The compact, slim body easily navigates under furniture and in tight spaces where traditional vacuums struggle.'),
    'crevice-tips': ('Versatile Cleaning Tools', 'Specialized crevice and cleaning tools reach every corner and surface for a thorough, complete clean.'),
    '5-step-filtration': ('5-Step Filtration System', 'Five layers of filtration capture 99.99% of fine dust and allergens, releasing only clean air back into your home.'),
    'easy-detachable': ('Easy-Detachable Filters', 'Washable filters are simple to remove and clean, maintaining peak suction performance with minimal effort.'),
    'convenience': ('All-in-One Tower Charger', 'The tower charger conveniently stores and charges the vacuum and accessories in one organized station.'),
    'design-1': ('Elegant Design', 'Sophisticated design in Calming Green or Cream White seamlessly blends into modern home interiors.'),
}
for ft in a9l.get('features', []):
    fn = ft['p'].split('/')[-1]
    for key, (title, desc) in feat_title_map.items():
        if key in fn:
            ft['t'] = title
            ft['d'] = desc
            if not ft.get('a') or ft['a'] == ft.get('t',''):
                ft['a'] = title
            break

with open(f'{BASE}/bulk_data.json', 'w', encoding='utf-8') as f:
    json.dump(bulk, f, ensure_ascii=False, indent=1)
print('bulk_data.json updated.')

# Show final A9LSLIM state
print(f'\nA9LSLIM final: gal={len(a9l["gallery"])}, feat={len(a9l["features"])}')
for ft in a9l['features']:
    print(f'  {ft["t"][:40]:40s} {ft["p"].split("/")[-1][:40]:40s} {ft.get("w","?")}x{ft.get("h","?")}')
