"""Find the REAL product gallery (white-bg multi-angle) for LSEL6333D.
The /images/ha/ STS series are all lifestyle/feature shots — not the product gallery."""
import re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/bulk_html/LSEL6333D.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1) ALL CDN images on page (full list)
print('=' * 70)
print('ALL non-rendition CDN image paths (categorized)')
print('=' * 70)
pat = re.compile(r'/content/dam/channel/wcms/sa_en[^\s"\'<>?]+\.(?:jpg|jpeg|png|webp|gif)', re.I)
all_paths = sorted(set(p.replace('/content/dam/channel/wcms/sa_en', '') for p in pat.findall(html)))

# Filter out renditions/thumbnails
clean = [p for p in all_paths if '/jcr:content/' not in p and '/renditions/' not in p]
print(f'  Clean paths: {len(clean)} (out of {len(all_paths)} total)')

# Group by folder
from collections import defaultdict
by_folder = defaultdict(list)
for p in clean:
    folder = '/'.join(p.split('/')[:-1])
    by_folder[folder].append(p.split('/')[-1])

for folder, files in sorted(by_folder.items()):
    print(f'\n  📁 {folder} ({len(files)} files)')
    for f in files[:30]:
        print(f'     {f}')
    if len(files) > 30:
        print(f'     ... and {len(files) - 30} more')

# 2) Specifically look for gallery-style paths
print('\n' + '=' * 70)
print('Gallery / product-shot pattern hunt')
print('=' * 70)
for kw in ['gallery', 'medium', 'large', '/d-', '450_basic', 'hr-images', 'product/', 'cooking-appliances/lsel']:
    matches = [p for p in clean if kw.lower() in p.lower()]
    if matches:
        print(f'\n  Keyword "{kw}" → {len(matches)} matches:')
        for m in matches[:20]:
            print(f'    {m}')

# 3) Look for og:image / link rel=preload (usually main product hero)
print('\n' + '=' * 70)
print('og:image and preload images')
print('=' * 70)
for pat_name, pat_re in [
    ('og:image', r'og:image"[^>]*content="([^"]+)"'),
    ('preload', r'<link[^>]*rel="preload"[^>]*href="([^"]+\.(?:jpg|jpeg|png|webp))"'),
    ('twitter:image', r'twitter:image"[^>]*content="([^"]+)"'),
]:
    matches = re.findall(pat_re, html)
    print(f'\n  {pat_name}: {len(matches)} matches')
    for m in matches[:5]:
        print(f'    {m}')

# 4) Find embedded image JSON in any script
print('\n' + '=' * 70)
print('Embedded image data')
print('=' * 70)
# LG often has galleryImageList or pdpImageList in JSON
for term in ['"galleryImage"', '"pdpImage"', '"productImage"', '"galleryImages"', '"galleryImage360"', '"imageList"', 'galleryImage', 'pdpImageBigUrl', 'pdpImage']:
    matches = re.findall(rf'{re.escape(term)}[^,]*?:\s*"([^"]+)"', html)
    if matches:
        print(f'\n  {term}: {len(matches)} matches')
        for m in matches[:8]:
            if m and len(m) > 5:
                print(f'    {m[:160]}')

# Dump 2000 chars around galleryImage if found
if 'galleryImage' in html:
    pos = html.find('galleryImage')
    print(f'\n--- galleryImage context (pos {pos}) ---')
    print(html[pos:pos+2000].replace('\\u003c', '<').replace('\\"', '"')[:2000])
