"""Crawl S90TR product data from LG Saudi Arabia."""
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

print('Fetching S90TR page...')
html = fetch('https://www.lg.com/sa_en/speakers/soundbars/s90tr/')
print(f'Page size: {len(html):,}')

chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
combined = ''.join(chunks).replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
print(f'next_f size: {len(combined):,}')

# Price
price_m = re.search(r'"price":"([0-9.]+)"', html)
price = float(price_m.group(1)) if price_m else 0
msrp_m = re.search(r'originalPrice[^0-9]*([0-9]+(?:\.[0-9]+)?)', combined)
msrp = float(msrp_m.group(1)) if msrp_m else None
print(f'Price: SAR {price}, MSRP: SAR {msrp}')

# All unique product image paths
all_paths = re.findall(r'(/(?:images|content/dam)[^"\\]+\.(?:jpg|png|webp))', combined)
seen_p = set()
unique_paths = []
for p in all_paths:
    base = p.split('/jcr:')[0].split('?')[0]
    rel = re.sub(r'.*/wcms/sa_en', '', base)
    if not rel: rel = base
    if re.search(r'gnb|banner|home-page|logo|favicon|spring|multishop|ministry', rel, re.I): continue
    if 's90tr' not in rel.lower(): continue
    if rel not in seen_p:
        seen_p.add(rel)
        unique_paths.append(rel)

print(f'Found {len(unique_paths)} unique product image paths')
for p in sorted(unique_paths):
    print(f'  {p}')
