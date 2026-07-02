"""Find embedded JSON spec data in LSEL6333D HTML."""
import re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/bulk_html/LSEL6333D.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1) Look for techSpecs / specName / specDesc strings in JSON body
print('=' * 70)
print('Spec data in embedded JSON')
print('=' * 70)

# Most LG pages have a __NEXT_DATA__ or similar JSON dump. Let's find them.
patterns = [
    (r'"techSpecs"\s*:\s*\[(\[.+?\])\s*\]', 'techSpecs array'),
    (r'"keySpec"\s*:\s*(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', 'keySpec object'),
    (r'"specName"\s*:\s*"([^"]+)"\s*,\s*"specDesc"\s*:\s*"([^"]*)"', 'specName/specDesc pairs'),
    (r'"specName"\s*:\s*"([^"]+)"', 'specName entries'),
    (r'"name"\s*:\s*"([^"]{2,80})"\s*,\s*"value"\s*:\s*"([^"]+)"', 'name/value pairs'),
]
for pat, label in patterns:
    matches = re.findall(pat, html)
    print(f'\n  {label}: {len(matches)} matches')
    for m in matches[:10]:
        if isinstance(m, tuple):
            print(f'    {m[0][:50]} : {str(m[1])[:80]}')
        else:
            print(f'    {str(m)[:200]}')

# 2) Look for spec in any deeply nested JSON literal
print('\n' + '=' * 70)
print('Look for "DIMENSIONS" or known spec headers in JSON')
print('=' * 70)
for hdr in ['DIMENSIONS', 'PERFORMANCE', 'FEATURES', 'GENERAL', 'POWER', 'CAPACITY']:
    matches = re.findall(rf'"({hdr}[^"]*)"', html, re.I)
    if matches:
        print(f'  {hdr}: {len(matches)} matches  e.g. {matches[:3]}')

# 3) Compare-selling spec table — look at full document for any spec markup
print('\n' + '=' * 70)
print('All h3 / h4 in spec section')
print('=' * 70)
spec_section = re.search(r'pdp-specs-section[^>]*>(.+?)pdp-review', html, re.S)
if spec_section:
    print(f'  Spec section size: {len(spec_section.group(1)):,}')
    headers = re.findall(r'<h[34][^>]*>(.+?)</h[34]>', spec_section.group(1), re.S)
    for h in headers[:30]:
        clean = re.sub(r'<[^>]+>', '', h).strip()
        clean = re.sub(r'\s+', ' ', clean)
        if clean:
            print(f'    {clean[:100]}')

# 4) Description / overview from JSON-LD
print('\n' + '=' * 70)
print('JSON-LD Product entries (full)')
print('=' * 70)
matches = re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html, re.S)
for i, m in enumerate(matches):
    try:
        data = json.loads(m)
        if isinstance(data, dict) and data.get('@type') == 'Product':
            print(f'\n  Block {i+1} (Product):')
            for k, v in data.items():
                if k in ('@type', '@context'):
                    continue
                if isinstance(v, (dict, list)):
                    print(f'    {k}: {str(v)[:150]}')
                else:
                    print(f'    {k}: {str(v)[:200]}')
    except Exception:
        pass

# 5) Find a sample of the embedded React data
print('\n' + '=' * 70)
print('Embedded data blocks (length > 5000)')
print('=' * 70)
for m in re.finditer(r'self\.__next_f\.push\(\[\d+,\s*"((?:[^"\\]|\\.)+)"\]\)', html):
    raw = m.group(1)
    if 'specName' in raw or 'techSpecs' in raw:
        # Find a small sample with specName
        spec_pos = raw.find('specName')
        if spec_pos > 0:
            print(f'  Found block (length {len(raw):,}):')
            print(f'  Context around specName: {raw[max(0,spec_pos-100):spec_pos+800]}')
            break
