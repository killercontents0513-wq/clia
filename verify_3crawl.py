"""Verify the 3 just-crawled products: LSEL6333D, LT19HBHSIN, S90TR"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
TARGETS = ['LSEL6333D', 'LT19HBHSIN', 'S90TR']

with open(PATH, 'r', encoding='utf-8') as f:
    html = f.read()

print('=' * 70)
print('FINAL VERIFICATION — 3 products')
print('=' * 70)

for code in TARGETS:
    idx = html.find(f'{{id:"{code}"')
    if idx < 0:
        print(f'\n{code}: NOT FOUND')
        continue
    nxt = html.find('{id:"', idx + 10)
    if nxt < 0:
        nxt = idx + 100000
    block = html[idx:nxt]

    gal_m = re.search(r'gal:\[(.*?)\]\s*,\s*feat:', block, re.S)
    feat_m = re.search(r'feat:\[(.*?)\]\s*,\s*sp:', block, re.S)
    sp_m = re.search(r'sp:\{(.*?)\}\s*,', block, re.S)
    pr_m = re.search(r'pr:"([^"]*)"', block)
    nm_m = re.search(r'nm:"([^"]+)"', block)

    g = gal_m.group(1) if gal_m else ''
    f_ = feat_m.group(1) if feat_m else ''
    s = sp_m.group(1) if sp_m else ''

    g_count = len(re.findall(r'\{a:"', g))
    f_count = len(re.findall(r'\{a:"', f_))
    s_count = len(re.findall(r'"[^"]+":"[^"]*"', s))

    # Sample first feature title for sanity
    first_feat_t = ''
    fm = re.search(r'\{a:"[^"]*",p:"[^"]*",t:"([^"]+)"', f_)
    if fm:
        first_feat_t = fm.group(1)[:50]

    print(f'\n{code}')
    print(f'  nm:           {(nm_m.group(1) if nm_m else "-")[:65]}')
    print(f'  pr:           SAR {pr_m.group(1) if pr_m else "-"}')
    print(f'  gal:          {g_count} images')
    print(f'  feat:         {f_count} entries')
    print(f'  sp:           {s_count} fields')
    print(f'  first feat t: {first_feat_t}')
    print(f'  block size:   {len(block):,} chars')

# Total status
print('\n' + '=' * 70)
crawled = html.count('crawled:true')
total = len(re.findall(r'^\{id:"', html, re.M))
print(f'Crawled flag: {crawled}/{total} products')

# Top order
matches = list(re.finditer(r'^\{id:"([^"]+)"', html, re.M))
top10 = [m.group(1) for m in matches[:10]]
print(f'Top 10 order: {top10}')
print('=' * 70)
