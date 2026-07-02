"""Fetch image dimensions (w, h) for all bulk_data.json products.
For deep-crawled products: copy w/h from deep_data.json.
For bulk-only products: partial-read image headers from LG CDN.
"""
import json, re, sys, io, struct, urllib.request, concurrent.futures as cf
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
CDN = 'https://www.lg.com/content/dam/channel/wcms/sa_en'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

def get_img_dims(url):
    """Fetch first 64KB of image and extract dimensions."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Range': 'bytes=0-65535'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
        # JPEG
        if data[:2] == b'\xff\xd8':
            i = 2
            while i < len(data) - 8:
                if data[i] != 0xff: break
                marker = data[i+1]
                if marker in (0xc0, 0xc1, 0xc2):
                    h = struct.unpack('>H', data[i+5:i+7])[0]
                    w = struct.unpack('>H', data[i+7:i+9])[0]
                    return w, h
                length = struct.unpack('>H', data[i+2:i+4])[0]
                i += 2 + length
        # PNG
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            w = struct.unpack('>I', data[16:20])[0]
            h = struct.unpack('>I', data[20:24])[0]
            return w, h
        # WebP
        if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            if data[12:16] == b'VP8L':
                bits = struct.unpack('<I', data[21:25])[0]
                w = (bits & 0x3FFF) + 1
                h = ((bits >> 14) & 0x3FFF) + 1
                return w, h
            elif data[12:16] == b'VP8 ':
                w = struct.unpack('<H', data[26:28])[0] & 0x3FFF
                h = struct.unpack('<H', data[28:30])[0] & 0x3FFF
                return w, h
        return 0, 0
    except Exception as e:
        return 0, 0

# Load data
with open(f'{BASE}/bulk_data.json', 'r', encoding='utf-8') as f:
    bulk = json.load(f)
with open(f'{BASE}/deep_data.json', 'r', encoding='utf-8') as f:
    deep_list = json.load(f)

# Build deep lookup: code -> {path -> (w, h)}
deep_dims = {}
for p in deep_list:
    code = p['code']
    dims = {}
    for img in p.get('gallery', []):
        if img.get('w') and img.get('h'):
            dims[img['p']] = (img['w'], img['h'])
    for img in p.get('features', []):
        if img.get('w') and img.get('h'):
            dims[img['p']] = (img['w'], img['h'])
    deep_dims[code] = dims

def add_dims_to_product(p):
    code = p['code']
    deep = deep_dims.get(code, {})
    imgs_to_fetch = []

    # Gallery
    for img in p.get('gallery', []):
        if 'w' in img: continue
        if img['p'] in deep:
            img['w'], img['h'] = deep[img['p']]
        else:
            imgs_to_fetch.append(('gal', img))

    # Features
    for feat in p.get('features', []):
        if 'w' in feat: continue
        if feat['p'] in deep:
            feat['w'], feat['h'] = deep[feat['p']]
        else:
            imgs_to_fetch.append(('feat', feat))

    # Fetch missing dims in parallel
    if imgs_to_fetch:
        def fetch_one(item):
            kind, img = item
            url = CDN + img['p']
            w, h = get_img_dims(url)
            return img, w, h

        with cf.ThreadPoolExecutor(max_workers=8) as ex:
            results = list(ex.map(fetch_one, imgs_to_fetch))

        for img, w, h in results:
            if w and h:
                img['w'] = w
                img['h'] = h

    # Count hits
    total = len(p.get('gallery',[])) + len(p.get('features',[]))
    with_dims = sum(1 for i in p.get('gallery',[]) if 'w' in i) + \
                sum(1 for i in p.get('features',[]) if 'w' in i)
    return code, with_dims, total

print(f'Processing {len(bulk)} products...')
for i, p in enumerate(bulk):
    code, hit, total = add_dims_to_product(p)
    print(f'  [{i+1:2d}/{len(bulk)}] {code:15s}: {hit}/{total} dims')

with open(f'{BASE}/bulk_data.json', 'w', encoding='utf-8') as f:
    json.dump(bulk, f, ensure_ascii=False, indent=1)

print(f'\nSaved bulk_data.json with dimensions!')
