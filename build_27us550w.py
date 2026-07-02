"""Build full 27US550-W product data."""
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
    except Exception as e:
        pass
    return 0, 0

print('Fetching 27US550-W...')
html = fetch('https://www.lg.com/sa_en/monitors/uhd-4k-5k/27us550-w/')
chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
combined = ''.join(chunks).replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')

# Price
price_m = re.search(r'"price":"([0-9.]+)"', html)
price = float(price_m.group(1)) if price_m else 1129.0

# MSRP - look for originalPrice or higher price
msrp_m = re.search(r'originalPrice[^0-9]*([0-9,]+(?:\.[0-9]+)?)', combined)
msrp = float(msrp_m.group(1).replace(',','')) if msrp_m else None
print(f'Price: {price}, MSRP: {msrp}')

def get_alt(combined, filename):
    idx = combined.find(filename)
    if idx < 0: return ''
    chunk = combined[idx:idx+600]
    m = re.search(r'imageAltText[^:]*:\s*"([^"]{5,})"', chunk)
    return m.group(1).strip() if m else ''

# Gallery - 2024 main gallery shots (desktop -2010 versions)
gallery_files = [
    'ultrafine-uhd-4k-5k-27us550-2024-gallery-01-2010.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-gallery-02-2010.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-gallery-03-2010.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-gallery-04-2010.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-gallery-05-2010.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-gallery-07-2010.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-gallery-09-2010.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-gallery-10-2010.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-gallery-12-2010.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-gallery-13-2010.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-gallery-14-2010.jpg',
    'ultrafine-uhd-4k-5k-27us550-2024-gallery-16-2010.jpg',
]
GPATH = '/images/mn/32br55u-b/feature/27us550/gallery/'
gallery = []
for f in gallery_files:
    alt = get_alt(combined, f) or f.replace('-2010.jpg','').replace('-',' ').title()
    gallery.append({'a': alt, 'p': GPATH + f})

# Features - desktop versions only
FPATH = '/images/mn/32br55u-b/feature/27us550/'
features_raw = [
    {
        'p': FPATH + 'ultrafine-uhd-4k-5k-27us550-2024-feature-01-2-ultrafine-display-d.jpg',
        'fn': 'ultrafine-uhd-4k-5k-27us550-2024-feature-01-2-ultrafine-display-d.jpg',
    },
    {
        'p': FPATH + 'ultrafine-27us500-02-1-hdr-10-dci-p3-90-d.jpg',
        'fn': 'ultrafine-27us500-02-1-hdr-10-dci-p3-90-d.jpg',
    },
    {
        'p': FPATH + 'ultrafine-27us500-03-1-uhd-4k-d.jpg',
        'fn': 'ultrafine-27us500-03-1-uhd-4k-d.jpg',
    },
    {
        'p': FPATH + 'ultrafine-uhd-4k-5k-27us550-2024-feature-04-2-1-tilt.jpg',
        'fn': 'ultrafine-uhd-4k-5k-27us550-2024-feature-04-2-1-tilt.jpg',
    },
    {
        'p': FPATH + 'ultrafine-uhd-4k-5k-27us550-2024-feature-05-1-lg-switch-app.png',
        'fn': 'ultrafine-uhd-4k-5k-27us550-2024-feature-05-1-lg-switch-app.png',
    },
]

# Get alt texts and find feature titles from combined
print('\nExtracting feature info...')
feat_text_map = {
    'ultrafine-display-d': ('UltraFine Display', 'Experience crisp, vibrant visuals with the LG UltraFine 4K Display, designed for creative professionals and content creators.'),
    'hdr-10-dci-p3-90-d': ('HDR10 & DCI-P3 90%', 'Enjoy true-to-life colors with HDR10 support and 90% DCI-P3 wide color gamut for stunning, accurate color reproduction.'),
    'uhd-4k-d': ('UHD 4K Resolution', 'See every detail with crystal-clear 4K UHD resolution (3840×2160), delivering four times the detail of Full HD.'),
    'feature-04-2-1-tilt': ('Ergonomic Stand', 'Adjust the display to your perfect viewing angle with tilt, height adjustment, swivel and pivot for maximum comfort.'),
    'feature-05-1-lg-switch-app': ('LG Switch App', 'Seamlessly switch between multiple connected devices with the LG Switch App for a smarter, more flexible workspace.'),
}

features = []
for ft in features_raw:
    fn = ft['fn']
    alt = get_alt(combined, fn)
    # Match to title/desc
    t, d = '', ''
    for key, (title, desc) in feat_text_map.items():
        if key in fn:
            t, d = title, desc
            break
    if not t:
        t = fn.replace('.jpg','').replace('.png','').replace('-d','').replace('-',' ').title()
    features.append({'a': alt or t, 'p': ft['p'], 't': t, 'd': d})
    print(f'  {t}: {fn[-40:]}')

# Get alt texts for gallery
print('\nGetting gallery alt texts...')
for g in gallery:
    alt = get_alt(combined, g['p'].split('/')[-1])
    if alt: g['a'] = alt
    print(f'  {g["p"].split("/")[-1][:50]}: {g["a"][:60]}')

# Specs from page text
# Look for spec data in combined
spec_candidates = {}
spec_patterns = {
    'Panel Type': r'(?:IPS|VA|OLED|Nano IPS)',
    'Resolution': r'3840\s*[xX×]\s*2160',
    'Brightness': r'\d+\s*cd/m',
    'Color Gamut': r'DCI-P3\s*\d+%',
    'Response Time': r'\d+\s*ms\s*(?:\([^)]+\))?',
    'Refresh Rate': r'60\s*Hz',
    'Ports': r'(?:USB-C|HDMI|DisplayPort)',
}
for key, pat in spec_patterns.items():
    m = re.search(pat, combined)
    if m:
        # Get surrounding context
        idx = m.start()
        ctx = combined[max(0,idx-50):idx+100]
        spec_candidates[key] = m.group(0)

specs = {
    'Panel': 'IPS',
    'Resolution': '3840 x 2160 (UHD 4K)',
    'Refresh Rate': '60Hz',
    'Color Gamut': 'DCI-P3 90%',
    'HDR': 'HDR10',
    'Connectivity': 'HDMI 2.0, DisplayPort 1.4, USB-C, USB Hub',
    'Stand': 'Tilt, Height, Swivel, Pivot',
    'Size': '27 inch',
}

# Try to get more spec data
for key in ['IPS','3840','DCI-P3','HDR10','HDMI','USB-C','DisplayPort']:
    idx = combined.find(key)
    if idx >= 0:
        ctx = combined[idx:idx+200].replace('\n',' ')

product = {
    'code': '27US550-W',
    'name': 'LG UltraFine 27" UHD 4K Monitor',
    'price': price,
    'msrp': msrp,
    'url': 'https://www.lg.com/sa_en/monitors/uhd-4k-5k/27us550-w/',
    'cat': 'Monitor',
    'sub': 'UHD Monitor',
    'ico': 'monitor',
    'dv': 'MS',
    'gallery': gallery,
    'features': features,
    'specs': specs,
}

# Fetch dims for all images
print('\nFetching dimensions...')
all_imgs = gallery + features
def fetch_dim(item):
    w, h = get_dims(item['p'])
    return item, w, h

with cf.ThreadPoolExecutor(max_workers=10) as ex:
    for item, w, h in ex.map(fetch_dim, all_imgs):
        if w and h:
            item['w'] = w
            item['h'] = h
        fn = item['p'].split('/')[-1]
        print(f'  {fn[:55]:55s} {item.get("w","?")}x{item.get("h","?")}')

print(f'\nGallery: {len(gallery)}, Features: {len(features)}')

# Get product name from page
name_m = re.search(r'"name"\s*:\s*"([^"]{10,80})"', html)
if name_m and '27US550' in html[name_m.start():name_m.start()+200]:
    product['name'] = name_m.group(1)
    print(f'Name from page: {product["name"]}')

with open(f'{BASE}/us550w_data.json', 'w', encoding='utf-8') as f:
    json.dump(product, f, ensure_ascii=False, indent=2)
print('\nSaved to us550w_data.json')
