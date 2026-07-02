# -*- coding: utf-8 -*-
# Make v6_18.html self-contained by inlining referenced local assets as base64 data URIs.
import base64, os, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
HTML = f'{BASE}/LG_AI_Content_Hub_v6_18.html'
ASSETS = f'{BASE}/amazon-aplus/assets'

# Files to embed (original relative path → absolute path on disk)
FILES = {
    'amazon-aplus/assets/lg-logo-dark.png':    f'{ASSETS}/lg-logo-dark.png',
    'amazon-aplus/assets/lg-logo-symbol.png':  f'{ASSETS}/lg-logo-symbol.png',
}

def to_data_uri(path):
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    ext = os.path.splitext(path)[1].lstrip('.').lower()
    mime = {'png':'image/png','jpg':'image/jpeg','jpeg':'image/jpeg','svg':'image/svg+xml'}.get(ext, 'application/octet-stream')
    return f'data:{mime};base64,{b64}'

# Build replacements
repls = {}
for rel, absp in FILES.items():
    if not os.path.exists(absp):
        print(f'[WARN] missing {absp}')
        continue
    uri = to_data_uri(absp)
    sz = len(uri)
    print(f'  {rel}: {os.path.getsize(absp):,} bytes → {sz:,} base64 chars')
    repls[rel] = uri

# Load HTML
with open(HTML, encoding='utf-8') as f:
    html = f.read()

# Backup before edit
bk = HTML.replace('.html','.pre_embed.html')
with open(bk,'w',encoding='utf-8') as f: f.write(html)
print(f'backup: {bk}')

# Count occurrences before
for rel in repls:
    n = html.count(rel)
    print(f'  "{rel}" occurs {n}× in HTML')

# Replace
new_html = html
for rel, uri in repls.items():
    new_html = new_html.replace(rel, uri)

# Verify no leftover local refs
leftover = re.findall(r'["\'](amazon-aplus/assets/[^"\']+)["\']', new_html)
if leftover:
    print(f'[WARN] leftover local refs: {set(leftover)}')
else:
    print('[OK] no local asset refs remain')

# Size delta
print(f'\nsize: {len(html):,} → {len(new_html):,} ({len(new_html)-len(html):+,} chars)')

# Write
with open(HTML, 'w', encoding='utf-8') as f:
    f.write(new_html)
print(f'wrote: {HTML}')
