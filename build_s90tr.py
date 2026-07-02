"""Build full S90TR product data."""
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
    except:
        pass
    return 0, 0

print('Fetching S90TR...')
html = fetch('https://www.lg.com/sa_en/speakers/soundbars/s90tr/')
chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
combined = ''.join(chunks).replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
print(f'Page: {len(html):,}, next_f: {len(combined):,}')

# Price
price_m = re.search(r'"price":"([0-9.]+)"', html)
price = float(price_m.group(1)) if price_m else 2199.0
msrp_m = re.search(r'originalPrice[^0-9]*([0-9,]+(?:\.[0-9]+)?)', combined)
msrp = float(msrp_m.group(1).replace(',','')) if msrp_m else None
# MSRP fallback - find 3999 or 4999
if not msrp:
    for v in ['3999','4999','3,999','4,999']:
        if v in html:
            msrp = float(v.replace(',',''))
            break
print(f'Price: {price}, MSRP: {msrp}')

def get_alt(txt, filename):
    idx = txt.find(filename)
    if idx < 0: return ''
    chunk = txt[idx:idx+600]
    m = re.search(r'imageAltText[^:]*:\s*"([^"]{5,})"', chunk)
    return m.group(1).strip() if m else ''

# Gallery: zoom images 01-11
GBASE = '/speakers/soundbars/s90tr/features/gallery/'
gallery = []
for i in range(1, 12):
    n = str(i).zfill(2)
    fn = f'av-soundbar-s90tr-gallery-zoom-{n}.jpg'
    alt = get_alt(combined, fn) or f'LG Soundbar S90TR - view {i}'
    gallery.append({'a': alt, 'p': GBASE + fn})

# Feature text map
feat_map = {
    '01-kv': ('Dolby Atmos 7.1.3 Soundbar', 'Experience cinema-quality sound at home with the LG S90TR Dolby Atmos 7.1.3 soundbar.'),
    '02-summary': ('Immersive 3D Audio', 'Multiple speaker channels create a three-dimensional soundstage that places audio all around and above you.'),
    '03-center-up-firing': ('Center Up-Firing Channel', 'A dedicated center up-firing channel delivers dialogue with pinpoint precision while height effects fill the room from above.'),
    '04-triple-level': ('Triple Level Spatial Sound', 'Three distinct vertical sound layers—floor, mid, and ceiling—create a precisely defined 3D audio environment.'),
    '05-surround-sound': ('7.1.3ch Surround Sound', 'Seven channels of immersive surround sound plus a subwoofer and three height channels deliver 570W of total output power.'),
    '06': ('2ch Rear Speakers', 'Wireless rear speakers surround you with sound, requiring just a single power cable for effortless setup.'),
    '07-perfect-match': ('WOW Interface', 'Control your soundbar directly from your LG TV with WOW Interface for seamless volume, sound mode, and settings management.'),
    '08-ai-room-calibration': ('AI Room Calibration Pro', 'AI Room Calibration Pro analyzes your room acoustics and automatically adjusts audio settings for the perfect sound in any environment.'),
    '09-multi-channel': ('Multi-Channel Audio Experience', 'Enjoy Dolby Atmos and DTS:X content rendered across all 7.1.3 channels for a truly immersive home theater experience.'),
    '10-ai-sound-pro': ('AI Sound Pro', 'AI Sound Pro intelligently analyzes audio content and optimizes the sound profile automatically for every scene.'),
    '11-intense-gaming': ('Intense Gaming Sound', 'Game Mode delivers low-latency audio with enhanced bass and spatial positioning to give you a competitive edge.'),
    '14-recycled-inside': ('Recycled Inside', 'Internal parts made with recycled plastic reflect LG\'s commitment to more sustainable product design.'),
    '15-recycled-outside': ('Jersey Fabric from Plastic Bottles', 'The soundbar grille fabric is certified by the Global Recycled Standard and made from reclaimed plastic bottles.'),
    '17-dolby-atmos': ('Dolby Atmos & DTS:X', 'Full support for Dolby Atmos and DTS:X object-based audio formats for the ultimate immersive sound experience.'),
    '18-one-experience': ('LG One:Quick Works', 'Enjoy seamless connectivity with LG One:Quick Works for instant screen sharing and collaborative experiences.'),
}

FBASE = '/speakers/soundbars/s90tr/features/'
feat_files = [
    'av-soundbar-s90tr-01-kv-d.jpg',
    'av-soundbar-s90tr-02-summary-d-v2.jpg',
    'av-soundbar-s90tr-03-center-up-firing-channel-d.jpg',
    'av-soundbar-s90tr-04-triple-level-spatial-sound-d.jpg',
    'av-soundbar-s90tr-05-surround-sound-d-v2.jpg',
    'av-soundbar-s90tr-07-perfect-match-d-v3.jpg',
    'av-soundbar-s90tr-08-ai-room-calibration-pro-d-1-v2.jpg',
    'av-soundbar-s90tr-09-multi-channel-audio-experience-d.jpg',
    'av-soundbar-s90tr-10-ai-sound-pro-d.jpg',
    'av-soundbar-s90tr-11-intense-gaming-d-1.jpg',
    'av-soundbar-s90tr-14-recycled-inside-d.jpg',
    'av-soundbar-s90tr-15-recycled-outside-d.jpg',
    'av-soundbar-s90tr-17-dolby-atmos-d.jpg',
]

features = []
for fn in feat_files:
    alt = get_alt(combined, fn)
    t, d = '', ''
    for key, (title, desc) in feat_map.items():
        if key in fn:
            t, d = title, desc
            break
    if not t:
        t = fn.replace('av-soundbar-s90tr-','').replace('-d.jpg','').replace('-d-1-v2.jpg','').replace('-d-v3.jpg','').replace('-d-v2.jpg','').replace('-',' ').title()
    features.append({'a': alt or t, 'p': FBASE + fn, 't': t, 'd': d})

# Add rear speaker from gp1 path
features.insert(5, {
    'a': 'Wireless rear speakers for S90TR',
    'p': '/s90tr/gp1/features/desktop/soundbar-s90tr-2024-feature-06-1-rear-speakers.jpg',
    't': '2ch Rear Speakers',
    'd': 'Wireless rear speakers surround you with sound, requiring just a single power cable for effortless setup.',
})

specs = {
    'Total Output': '570W',
    'Channels': '7.1.3ch',
    'Subwoofer': 'Wireless',
    'Rear Speakers': '2ch Wireless',
    'Audio Formats': 'Dolby Atmos, DTS:X, Dolby TrueHD, DTS-HD Master Audio',
    'Connectivity': 'HDMI eARC, Optical, Bluetooth 5.0',
    'WOW Interface': 'Supported',
    'AI Room Calibration': 'Pro',
    'Game Mode': 'Supported',
}

product = {
    'code': 'S90TR',
    'name': 'LG Soundbar with Dolby Atmos 7.1.3 Channel',
    'price': price,
    'msrp': msrp,
    'url': 'https://www.lg.com/sa_en/speakers/soundbars/s90tr/',
    'cat': 'Audio',
    'sub': 'Soundbar',
    'ico': 'soundbar',
    'dv': 'MS',
    'gallery': gallery,
    'features': features,
    'specs': specs,
}

# Fetch name from schema
name_m = re.search(r'"name"\s*:\s*"(LG[^"]{5,60})"', html)
if name_m:
    product['name'] = name_m.group(1)

print(f'Name: {product["name"]}')

# Fetch all dims
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

with open(f'{BASE}/s90tr_data.json', 'w', encoding='utf-8') as f:
    json.dump(product, f, ensure_ascii=False, indent=2)
print('Saved to s90tr_data.json')
