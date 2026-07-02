"""Fresh download + inspect what's actually on LT19HBHSIN and LSEL6333D LG.com pages.
Goal: figure out the correct gallery/feature image patterns and feature/spec text."""
import re, sys, io, urllib.request, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

TARGETS = [
    ('LT19HBHSIN', 'https://www.lg.com/sa_en/refrigerators/top-freezers/lt19hbhsin/'),
    ('LSEL6333D', 'https://www.lg.com/sa_en/cooking-appliances/electric-cookers/lsel6333d/'),
]

CDN_PREFIX = '/content/dam/channel/wcms/sa_en'

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode('utf-8', errors='ignore')

def extract_jsonld(html):
    """Extract product schema from JSON-LD"""
    matches = re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html, re.S)
    for m in matches:
        try:
            data = json.loads(m)
            if isinstance(data, dict) and data.get('@type') == 'Product':
                return data
        except Exception:
            pass
    return {}

def extract_all_cdn_images(html):
    """All sa_en CDN image references (jpg/jpeg/png/webp)"""
    pat = re.compile(r'/content/dam/channel/wcms/sa_en/[^\s"\'<>?]+\.(?:jpg|jpeg|png|webp|gif)', re.I)
    raw = set(pat.findall(html))
    # Strip CDN prefix
    paths = [p.replace(CDN_PREFIX, '') for p in raw]
    return sorted(set(paths))

def extract_specs(html):
    """c-compare-selling__spec-name + spec-desc"""
    pat = re.compile(r'c-compare-selling__spec-name"><p>(.*?)</p>.*?c-compare-selling__spec-desc"><p>(.*?)</p>', re.S)
    out = {}
    for k, v in pat.findall(html):
        k = re.sub(r'<[^>]+>', '', k).strip()
        v = re.sub(r'<[^>]+>', '', v).strip()
        if k and v:
            out[k] = v
    return out

def extract_feature_blocks(html):
    """Find feature headline + body pairs"""
    # Common LG patterns
    headlines = re.findall(r'c-text-contents__headline[^>]*>([^<]+)</', html)
    bodies = re.findall(r'c-text-contents__body[^>]*>(.+?)</', html, re.S)
    return headlines, bodies

for code, url in TARGETS:
    print('=' * 75)
    print(f'  {code}')
    print(f'  {url}')
    print('=' * 75)

    try:
        html = fetch(url)
    except Exception as e:
        print(f'  FETCH FAILED: {e}')
        continue

    # Save fresh copy
    out_path = f'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/bulk_html/{code}.html'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  Saved to {out_path} ({len(html):,} chars)')

    # JSON-LD
    jsonld = extract_jsonld(html)
    name = jsonld.get('name', '?')
    print(f'\n  Name: {name}')
    offers = jsonld.get('offers', {})
    if isinstance(offers, dict):
        print(f'  Price: {offers.get("price", "?")}')
        ps = offers.get('priceSpecification', {})
        if isinstance(ps, dict):
            print(f'  MSRP: {ps.get("price", "?")}')

    # All CDN images
    paths = extract_all_cdn_images(html)
    print(f'\n  Total CDN images found: {len(paths)}')

    # Filter by code-related paths
    code_low = code.lower()
    relevant = [p for p in paths if code_low in p.lower()]
    print(f'  Code-related paths ({len(relevant)}):')
    for p in relevant[:60]:
        print(f'    {p}')
    if len(relevant) > 60:
        print(f'    ... and {len(relevant) - 60} more')

    # Categorize
    galleries = [p for p in relevant if '/gallery/' in p.lower()]
    features = [p for p in relevant if 'feature' in p.lower() and '/gallery/' not in p.lower()]
    print(f'\n  Galleries: {len(galleries)}')
    for p in galleries:
        print(f'    {p}')
    print(f'\n  Features: {len(features)}')
    for p in features:
        print(f'    {p}')

    # Specs
    specs = extract_specs(html)
    print(f'\n  Specs extracted: {len(specs)} fields')
    for k, v in list(specs.items())[:25]:
        print(f'    {k}: {v[:80]}')

    # Feature texts
    headlines, bodies = extract_feature_blocks(html)
    print(f'\n  Headline candidates: {len(headlines)}')
    for h in headlines[:15]:
        print(f'    "{h.strip()[:90]}"')

    print('\n')
