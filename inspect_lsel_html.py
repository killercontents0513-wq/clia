"""Deep inspect LSEL6333D HTML structure to find correct feature/spec patterns."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/bulk_html/LSEL6333D.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f'HTML size: {len(html):,}')

# Look for spec-related class patterns
print('\n--- Spec-related class patterns ---')
spec_classes = set(re.findall(r'class="([^"]*spec[^"]*)"', html, re.I))
for c in sorted(spec_classes)[:30]:
    print(f'  {c}')

print('\n--- "Specifications" or "Features" headers ---')
for m in re.finditer(r'(?:Specifications?|Features|Key\s+Features|Tech\s+Spec)', html, re.I):
    ctx = html[max(0, m.start()-50):m.end()+100]
    ctx = re.sub(r'\s+', ' ', ctx)[:200]
    print(f'  ...{ctx}...')

# All thru <dl>, <table>, key-value patterns
print('\n--- All headline candidates near LSEL6333D-STS images ---')
for m in re.finditer(r'LSEL6333D-STS-\d+(?:-\d+)?-(?:desktop|mobile)', html):
    pos = m.start()
    nearby = html[max(0, pos-1500):pos+300]
    # Find headline patterns nearby
    h_matches = re.findall(r'<h[1-6][^>]*>([^<]+)</h[1-6]>', nearby)
    if h_matches:
        for h in h_matches[-3:]:
            print(f'  near {m.group()}: H = "{h.strip()[:80]}"')
        break  # just one example

# Look for c-text or content classes
print('\n--- text-content classes ---')
text_classes = set(re.findall(r'class="((?:c-|s-|cmp-)[^"]*(?:title|head|body|text|content)[^"]*)"', html))
for c in sorted(text_classes)[:30]:
    print(f'  {c}')

# Sample search: specs as <dt>/<dd>?
print('\n--- <dt><dd> or table-row patterns ---')
dl_match = re.search(r'<dl[^>]*>(.{100,3000}?)</dl>', html, re.S)
if dl_match:
    print(f'  Found <dl>: {dl_match.group(1)[:500]}')

# JSON-LD raw
print('\n--- ld+json blocks ---')
for i, m in enumerate(re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html, re.S)):
    snippet = m.group(1)[:500]
    print(f'  Block {i+1}: {snippet}')
    if i >= 2: break

# Search for product name in the actual HTML
print('\n--- Title/h1 ---')
title = re.search(r'<title>([^<]+)</title>', html)
if title:
    print(f'  <title>: {title.group(1).strip()}')
h1 = re.findall(r'<h1[^>]*>(.{1,200}?)</h1>', html, re.S)
for h in h1[:3]:
    h_clean = re.sub(r'<[^>]+>', '', h).strip()
    h_clean = re.sub(r'\s+', ' ', h_clean)
    print(f'  <h1>: {h_clean[:200]}')

# Price patterns
print('\n--- Price patterns ---')
for pat in [r'SAR\s*[\d,\.]+', r'data-price="[^"]+"', r'"price"\s*:\s*"[^"]+"', r'priceCurrency']:
    matches = re.findall(pat, html)[:3]
    if matches:
        print(f'  {pat}: {matches}')
