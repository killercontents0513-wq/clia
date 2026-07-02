"""Targeted inspection of LSEL6333D for spec/feature extraction patterns."""
import re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/bulk_html/LSEL6333D.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1) Key Features list (c-floating-features keyFeatureList)
print('=' * 70)
print('KEY FEATURES list')
print('=' * 70)
m = re.search(r'id="keyFeatureList"[^>]*>(.+?)</ul>', html, re.S)
if m:
    items = re.findall(r'<li[^>]*>(.+?)</li>', m.group(1), re.S)
    for it in items:
        clean = re.sub(r'<[^>]+>', ' ', it)
        clean = re.sub(r'\s+', ' ', clean).strip()
        print(f'  • {clean[:200]}')
else:
    print('  (keyFeatureList not found)')

# 2) c-compare-selling__spec patterns
print('\n' + '=' * 70)
print('c-compare-selling specs')
print('=' * 70)
# Try multiple pattern variants
for pname, pat in [
    ('strict 1', r'c-compare-selling__spec-name"><p>(.*?)</p>.*?c-compare-selling__spec-desc"><p>(.*?)</p>'),
    ('strict 2', r'c-compare-selling__spec-name[^>]*>(.*?)<.*?c-compare-selling__spec-desc[^>]*>(.*?)<'),
    ('loose',    r'class="[^"]*spec-name[^"]*"[^>]*>(.*?)<.*?class="[^"]*spec-desc[^"]*"[^>]*>(.*?)<'),
]:
    matches = re.findall(pat, html, re.S)
    print(f'  Pattern "{pname}": {len(matches)} matches')
    for k, v in matches[:5]:
        k_clean = re.sub(r'<[^>]+>', '', k).strip()
        v_clean = re.sub(r'<[^>]+>', '', v).strip()
        print(f'    - {k_clean[:50]} : {v_clean[:80]}')

# 3) Search for spec areas
print('\n' + '=' * 70)
print('Spec areas (c-all-specs-area)')
print('=' * 70)
m = re.search(r'class="c-all-specs-area[^"]*"[^>]*>(.+?)</div>\s*</div>\s*</div>', html, re.S)
if m:
    snippet = m.group(1)[:1500]
    print(f'  Snippet: {snippet[:1500]}')

# 4) Headlines near LSEL6333D-STS images
print('\n' + '=' * 70)
print('Text near each STS image')
print('=' * 70)
sts_images = ['STS-02', 'STS-03', 'STS-07', 'STS-08']  # the main feature images
for code in sts_images:
    print(f'\n  Looking for context around {code}-desktop.jpg:')
    pos = html.find(f'{code}-desktop.jpg')
    if pos < 0:
        print('    (not found)')
        continue
    # Look back 4000 chars for any descriptive text
    nearby = html[max(0, pos-4000):pos]
    # Find h2/h3 near the image
    headers = re.findall(r'<h[23][^>]*>(.{1,150}?)</h[23]>', nearby, re.S)
    for h in headers[-3:]:
        h_clean = re.sub(r'<[^>]+>', '', h).strip()
        h_clean = re.sub(r'\s+', ' ', h_clean)
        print(f'    H near {code}: "{h_clean[:120]}"')

# 5) JSON-LD raw
print('\n' + '=' * 70)
print('JSON-LD product info')
print('=' * 70)
matches = re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html, re.S)
for i, m in enumerate(matches):
    try:
        data = json.loads(m)
        if isinstance(data, dict):
            t = data.get('@type', '')
            if t == 'Product':
                name = data.get('name', '?')
                offers = data.get('offers', {})
                price = '?'
                msrp = '?'
                if isinstance(offers, dict):
                    price = offers.get('price', '?')
                    ps = offers.get('priceSpecification', {})
                    if isinstance(ps, dict):
                        msrp = ps.get('price', '?')
                desc = data.get('description', '')[:200]
                print(f'  Product:')
                print(f'    name: {name}')
                print(f'    price: {price}, msrp: {msrp}')
                print(f'    description: {desc}')
    except Exception as e:
        pass

# 6) Find product description / overview text
print('\n' + '=' * 70)
print('Product description / overview blocks')
print('=' * 70)
# Some LG pages have c-text-contents with LG class names
for cls in ['c-text-contents__headline', 'c-text-contents__body', 'cmp-text', 's-detail__title', 's-detail__copy']:
    matches = re.findall(rf'class="[^"]*{re.escape(cls)}[^"]*"[^>]*>(.+?)</', html, re.S)
    print(f'\n  Class "{cls}": {len(matches)} matches')
    for snippet in matches[:5]:
        clean = re.sub(r'<[^>]+>', ' ', snippet)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if clean and len(clean) > 5:
            print(f'    "{clean[:120]}"')
