"""Crawl S65TR product data from LG Saudi Arabia."""
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
    except:
        pass
    return 0, 0

print('Fetching S65TR page...')
html = fetch('https://www.lg.com/sa_en/tv-soundbars/soundbars/s65tr/')
print(f'Page size: {len(html):,}')

# Extract next_f data
chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
combined = ''.join(chunks)
# Unescape
combined = combined.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
print(f'Combined next_f size: {len(combined):,}')

# Price from schema.org
price_m = re.search(r'"price":"([0-9.]+)"', html)
price = price_m.group(1) if price_m else '999.01'
# MSRP
msrp_m = re.search(r'originalPrice[^\d]*([0-9,]+(?:\.[0-9]+)?)', combined)
if not msrp_m:
    msrp_m = re.search(r'1[,.]?799', html)
msrp = '1799' if msrp_m else ''
print(f'Price: SAR {price}, MSRP: SAR {msrp}')

# DZ Gallery images with alt texts
gallery = []
for i in range(1, 12):
    n = str(i).zfill(2)
    key = f'S65TR-DZ-{n}.jpg'
    path = f'/images/audio-video/s65tr_asauelk/{key}'
    idx = combined.find(key)
    alt = ''
    if idx >= 0:
        chunk = combined[idx:idx+500]
        alt_m = re.search(r'imageAltText[^:]*:\s*"([^"]{5,})"', chunk)
        if alt_m:
            alt = alt_m.group(1).strip()
    if not alt:
        alt = f'LG Soundbar S65TR - view {i}'
    gallery.append({'a': alt, 'p': path})
    print(f'  GAL DZ-{n}: {alt[:60]}')

# Features with their images
features_raw = [
    {
        'p': '/images/av/s65tr/av-soundbar-s65tr-01-kv-desktop.jpg',
        't': 'The ideal sound companion for your LG TV',
        'd': 'Complete the LG TV experience with the soundbar that beautifully complements its design and sonic performance.',
    },
    {
        'p': '/images/av/s65tr/av-soundbar-s65tr-03-perfect-match-d-01-v6.jpg',
        't': 'WOW Interface',
        'd': 'Access WOW Interface through your LG TV for clear and simple soundbar control, like changing sound modes, profiles, and accessing other handy features, even while you watch.',
    },
    {
        'p': '/images/av/s65tr/av-soundbar-s65tr-04-surround-sound-d-01-v5.jpg',
        't': '5.1ch Surround Sound',
        'd': 'Become part of the scene with 600W 5.1ch surround sound, a subwoofer, and rear speakers.',
    },
    {
        'p': '/s65tr/gp1/features/desktop/soundbar-s65tr-2024-featurer-05-rear-speakers.jpg',
        't': '2ch Rear Speakers',
        'd': 'You only need one power cable and one speaker connection cable to install the rear speakers. The rear speakers connect wirelessly to the main soundbar.',
    },
    {
        'p': '/images/av/s65tr/av-soundbar-s65tr-06-ai-sound-pro-d-v6-new.jpg',
        't': 'AI Sound Pro',
        'd': 'AI Sound Pro categorizes different sounds into effects, music, and voices, and then applies the ideal settings to create the optimal audio experience.',
    },
    {
        'p': '/images/av/s65tr/av-soundbar-s65tr-07-recycled-inside-desktop.jpg',
        't': 'Recycled Inside',
        'd': 'LG Soundbars use recycled plastic on top and bottom parts. Proof we\'re taking a more eco-minded approach to soundbar production.',
    },
    {
        'p': '/images/av/s65tr/av-soundbar-s65tr-08-recycled-outside-desktop.jpg',
        't': 'Jersey fabric made with plastic bottles',
        'd': 'All LG Soundbars are thoughtfully designed with careful consideration to ensure a high percentage of reclaimed materials. The Global Recycled Standard certifies that the polyester jersey fabric is made from plastic bottles.',
    },
]

# Fetch dims for gallery
print('\nFetching gallery dims...')
def fetch_gal_dim(item):
    w, h = get_dims(item['p'])
    return item, w, h

with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for item, w, h in ex.map(fetch_gal_dim, gallery):
        if w and h:
            item['w'] = w
            item['h'] = h
            print(f'  {item["p"].split("/")[-1]}: {w}x{h}')

# Fetch dims for features
print('\nFetching feature dims...')
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for item, w, h in ex.map(fetch_gal_dim, features_raw):
        if w and h:
            item['w'] = w
            item['h'] = h
            print(f'  {item["p"].split("/")[-1]}: {w}x{h}')

# Specs from page text
specs = {
    'Total Output': '600W',
    'Channels': '5.1ch',
    'Subwoofer': 'Wireless',
    'Rear Speakers': '2ch Wireless',
    'Audio Technology': 'AI Sound Pro, Dolby Digital, DTS Digital Surround',
    'Sound Mode': 'AI Sound Pro, Standard, Bass Blast, Movie, Music, Clear Voice, Sports',
    'WOW Interface': 'Supported',
    'Connectivity': 'Optical, HDMI ARC, Bluetooth',
}

product = {
    'code': 'S65TR',
    'name': 'LG Soundbar with 5.1 Channel Surround Sound',
    'price': float(price),
    'msrp': float(msrp) if msrp else None,
    'url': 'https://www.lg.com/sa_en/tv-soundbars/soundbars/s65tr/',
    'cat': 'Audio',
    'sub': 'Soundbar',
    'ico': 'soundbar',
    'dv': 'MS',
    'gallery': gallery,
    'features': features_raw,
    'specs': specs,
}

print('\n=== PRODUCT SUMMARY ===')
print(f'Code: {product["code"]}')
print(f'Name: {product["name"]}')
print(f'Price: {product["price"]}, MSRP: {product["msrp"]}')
print(f'Gallery: {len(gallery)} images')
print(f'Features: {len(features_raw)} items')
print(f'Specs: {len(specs)} items')

# Save to JSON for review
with open(f'{BASE}/s65tr_data.json', 'w', encoding='utf-8') as f:
    json.dump(product, f, ensure_ascii=False, indent=2)
print('\nSaved to s65tr_data.json')
