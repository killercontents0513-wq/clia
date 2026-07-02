#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import json
import re
import struct
import os
import sys
from concurrent.futures import ThreadPoolExecutor

# CONFIG
CODE = "RNC7"
URL = "https://www.lg.com/sa_en/speakers/party-speakers/rnc7/"
CATEGORY = "speakers"

# STEP 1: DOWNLOAD
print(f"[Step 1] Downloading {CODE} from LG.com...")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
req = urllib.request.Request(URL, headers={"User-Agent": UA})
try:
    with urllib.request.urlopen(req, timeout=40) as r:
        raw = r.read()
    html = raw.decode('utf-8', errors='replace')
    os.makedirs("bulk_html", exist_ok=True)
    with open(f"bulk_html/{CODE}.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Downloaded {len(html)} chars to bulk_html/{CODE}.html")
except Exception as e:
    print(f"[FAIL] {e}")
    sys.exit(1)

# STEP 2: JSON-LD METADATA
print("[Step 2] Extracting JSON-LD metadata...")
meta = {}
try:
    m = re.search(r'<script[^>]+type="application/ld\+json"[^>]*>([^<]+)</script>', html)
    if m:
        data = json.loads(m.group(1))
        meta['name'] = data.get('name', '')
        meta['desc'] = data.get('description', '')
        if 'offers' in data and isinstance(data['offers'], list) and data['offers']:
            offer = data['offers'][0]
            meta['price'] = offer.get('price', '')
            meta['currency'] = offer.get('priceCurrency', 'SAR')
            if 'priceSpecification' in offer:
                meta['msrp'] = offer['priceSpecification'].get('price', '')
        print(f"[OK] Name: {meta.get('name', 'N/A')[:60]}")
        print(f"[OK] Price: {meta.get('currency')} {meta.get('price')}")
except Exception as e:
    print(f"[WARN] JSON-LD error: {e}")

# STEP 3: CDN IMAGES
print("[Step 3] Extracting CDN images...")
all_images = {}

# Pattern 1: Full HTTPS URLs
pattern1 = r'https://www\.lg\.com/content/dam/channel/wcms/sa_en/images/([^"\s?]+\.(jpg|jpeg|png|webp|gif))'
for match in re.finditer(pattern1, html):
    path = match.group(1)
    if any(x in path for x in ['renditions', 'jcr:content', 'gnb', 'home-page', 'banners-20', 'ai-core-tech']):
        continue
    all_images[path] = f"https://www.lg.com/content/dam/channel/wcms/sa_en/images/{path}"

# Pattern 2: Relative URLs
pattern2 = r'/content/dam/channel/wcms/sa_en/images/([^"\s?\\]+\.(jpg|jpeg|png|webp|gif))'
for match in re.finditer(pattern2, html):
    path = match.group(1)
    if any(x in path for x in ['renditions', 'jcr:content', 'gnb', 'home-page', 'banners-20', 'ai-core-tech']):
        continue
    if path not in all_images:
        all_images[path] = f"https://www.lg.com/content/dam/channel/wcms/sa_en/images/{path}"

print(f"[OK] Found {len(all_images)} unique images")

# STEP 4-5: CLASSIFY
print("[Step 4-5] Classifying gallery vs features...")
gal_paths = {k: v for k, v in all_images.items() if '/gallery/' in k and re.search(r'[SD]-\d{2}\.jpg', k)}
feat_paths = {k: v for k, v in all_images.items() if '/features/' in k}

def sort_gallery_key(item):
    filename = item[0].split('/')[-1]
    match = re.search(r'([A-Z])-(\d+)', filename)
    if match:
        prefix = match.group(1)
        num = int(match.group(2))
        return (prefix, num)
    return (filename, 0)

gal_sorted = sorted(gal_paths.items(), key=sort_gallery_key)
print(f"[OK] Gallery: {len(gal_paths)} images")
print(f"[OK] Features: {len(feat_paths)} images")

# STEP 6: DIMENSIONS
print("[Step 6] Fetching dimensions...")
def get_dims(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = r.read(65536)
        if data[:2] == b'\xff\xd8':
            sof = data.find(b'\xff\xc0') if data.find(b'\xff\xc0') >= 0 else data.find(b'\xff\xc1')
            if sof >= 0 and sof + 8 < len(data):
                h, w = struct.unpack('>HH', data[sof+5:sof+9])
                return (w, h)
        elif data[:8] == b'\x89PNG\r\n\x1a\n' and len(data) >= 24:
            w, h = struct.unpack('>II', data[16:24])
            return (w, h)
        elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            return (1600, 900)
        elif data[:3] == b'GIF':
            return (1600, 900)
    except:
        pass
    return (0, 0)

dims = {}
with ThreadPoolExecutor(max_workers=15) as ex:
    futures = {ex.submit(get_dims, url): path for path, url in gal_sorted}
    for i, future in enumerate(futures):
        path = futures[future]
        try:
            dims[path] = future.result()
        except:
            dims[path] = (0, 0)
        if (i+1) % 5 == 0:
            print(f"  {i+1}/{len(gal_sorted)} done")

print(f"[OK] Dimensions fetched")

# STEP 7: FEATURE TEXT
print("[Step 7] Extracting feature descriptions...")
feat_data = []
for path, url in sorted(feat_paths.items()):
    stem = path.split('/')[-1].rsplit('.', 1)[0]
    snippet_start = html.find(stem)
    snippet = html[max(0, snippet_start-3500):snippet_start+3500] if snippet_start >= 0 else ""
    title = ""
    desc = ""
    if snippet:
        h = re.search(r'c-text-contents__headline[^>]*>([^<]+)', snippet)
        if h:
            title = h.group(1).strip()
        d = re.search(r'c-text-contents__body[^>]*>([^<]+)', snippet)
        if d:
            desc = d.group(1).strip()
    if not title:
        title = stem.replace('-', ' ').replace('_', ' ').title()
    if not desc:
        desc = f"Feature: {title}"
    feat_data.append({
        'a': stem, 'p': url.replace('https://www.lg.com/content/dam/channel/wcms/sa_en/images/', '/images/'),
        't': title[:80], 'd': desc[:150], 'w': 1600, 'h': 900
    })

print(f"[OK] {len(feat_data)} features extracted")

# STEP 8: SPECS
print("[Step 8] Extracting specifications...")
specs = []
for match in re.finditer(r'c-compare-selling__spec-name"><p>(.*?)</p>.*?c-compare-selling__spec-desc"><p>(.*?)</p>', html, re.DOTALL):
    name, value = match.group(1).strip(), match.group(2).strip()
    if name and value:
        specs.append({'n': name[:100], 'v': value[:200]})

print(f"[OK] {len(specs)} specifications")

# SAVE
data = {
    'code': CODE, 'url': URL, 'name': meta.get('name', ''), 'price': meta.get('price', ''),
    'gal': [{'a': f"View {i+1}", 'p': path.replace(CATEGORY + '/', '').replace(CODE.lower() + '_dsauelk_emsj_sa_en_c/', ''),
             'w': dims[path][0], 'h': dims[path][1]} for i, (path, url) in enumerate(gal_sorted)],
    'feat': feat_data, 'sp': specs
}

with open('rnc7_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"[OK] rnc7_data.json written")
print(f"=== SUMMARY ===")
print(f"Product: {CODE}")
print(f"Gallery: {len(data['gal'])} images")
print(f"Features: {len(data['feat'])} items")
print(f"Specs: {len(data['sp'])} items")
print(f"Ready for: integrate_rnc7.py")
