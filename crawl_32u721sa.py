import urllib.request, re, json, struct, sys
sys.stdout.reconfigure(encoding='utf-8')

CODE = '32U721SA-W'
CDN  = 'https://www.lg.com/content/dam/channel/wcms/sa_en'
UA   = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

with open(f'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/bulk_html/{CODE}.html', 'r', encoding='utf-8') as f:
    html = f.read()

# --- Price ---
pr_val = ''
jld_blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
for j in jld_blocks:
    try:
        d = json.loads(j.strip())
        if isinstance(d, dict) and d.get('@type') == 'Product':
            offers = d.get('offers', {})
            if isinstance(offers, list): offers = offers[0]
            p = offers.get('price', '')
            if p:
                pf = float(p)
                pr_val = str(int(pf)) if pf == int(pf) else str(p)
    except:
        pass

if not pr_val:
    m = re.search(r'"price"\s*:\s*"?(\d[\d,.]+)"?', html)
    if m: pr_val = m.group(1)

print(f'Price: SAR {pr_val}')

# --- Name ---
nm_m = re.search(r'"name"\s*:\s*"([^"]+32[Uu]721[^"]*)"', html)
nm = nm_m.group(1) if nm_m else '32" UHD Smart Monitor | webOS | USB-C | HDR10'
print(f'Name: {nm}')

# --- Canonical probe ---
print('\n--- Canonical large01 probe ---')
gal_found = []
for cat in ['mn', 'monitors', 'smart-monitors']:
    for code in ['md08729574', '32u721sa', '32u721sa-w']:
        url = f'{CDN}/images/{cat}/{code}/gallery/large01.jpg'
        try:
            req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=5) as r:
                print(f'FOUND: images/{cat}/{code}/gallery/large01.jpg')
                for n in range(1, 16):
                    gal_found.append(f'/images/{cat}/{code}/gallery/large{n:02d}.jpg')
                break
        except:
            pass
    if gal_found:
        break

if not gal_found:
    print('Not found -> using gallery-XX-2010 pattern')

# --- Gallery ---
gal_raw = [
    'images/mn/32u721sa/gallery/smart-monitor-32u721sa-2025-gallery-gallery-01-2010.jpg',
    'images/mn/32u721sa/gallery/smart-monitor-32u721sa-2025-gallery-gallery-02-2010.jpg',
    'images/mn/32u721sa/gallery/smart-monitor-32u721sa-2025-gallery-gallery-03-2010.jpg',
    'images/mn/32u721sa/gallery/smart-monitor-32u721sa-2025-gallery-gallery-04-2010.jpg',
    'images/mn/32u721sa/gallery/smart-monitor-32u721sa-2025-gallery-gallery-05-2010.jpg',
    'images/mn/32u721sa/gallery/smart-monitor-32u721sa-2025-gallery-gallery-06-2010.jpg',
    'images/mn/32u721sa/gallery/smart-monitor-32u721sa-2025-gallery-gallery-07-2010.jpg',
    'images/mn/32u721sa/gallery/smart-monitor-32u721sa-2025-gallery-gallery-08-2010.jpg',
    'images/mn/32u721sa/gallery/smart-monitor-32u721sa-2025-gallery-gallery-09-2010.jpg',
    'images/mn/32u721sa/gallery/smart-monitor-32u721sa-2025-gallery-gallery-10.jpg',
]

# --- Feature images ---
feat_raw = [
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-01-3-intro-kv-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-02-1-summary-display-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-02-2-summary-mirroring-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-02-3-summary-productivity-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-02-4-summary-webos-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-03-2-display-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-04-2-webos-entertainment-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-05-1-webos-home-office-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-06-1-ai-brightness-control-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-07-1-dynamic-tone-mapping-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-08-1-simple-design-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-09-1-usb-c-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-10-1-thinq-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-11-1-easy-control-d.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-12-1-mirroing.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-13-1-lg-switch-app.jpg',
    'images/mn/32u721sa/smart-monitor-32u721sa-2025-feature-14-1-multi-ports.jpg',
]

def get_alt(p):
    fname = p.split('/')[-1]
    idx = html.find(fname)
    if idx == -1:
        return ''
    snip = html[max(0, idx-300):idx+200]
    m = re.search(r'alt="([^"]{3,})"', snip)
    return m.group(1) if m else ''

def get_title(p):
    fname = p.split('/')[-1]
    idx = html.find(fname)
    if idx == -1:
        return ''
    snip = html[max(0, idx-600):idx+300]
    m = re.search(r'c-text-contents__headline[^>]*>.*?<p[^>]*>(.*?)</p>', snip, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()[:100]
    m = re.search(r'<h[23][^>]*>(.*?)</h[23]>', snip, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()[:100]
    return ''

# Build gallery
print('\n--- Gallery ---')
gal_data = []
for p in gal_raw:
    a = get_alt(p)
    num = re.search(r'gallery-0?(\d+)', p)
    n = num.group(1) if num else '?'
    if not a:
        a = f'LG 32" UHD Smart Monitor 32U721SA-W — View {n}'
    gal_data.append({'p': '/' + p, 'a': a})
    print(f'  {n}: {a[:65]}')

# Build features
print('\n--- Features ---')
feat_data = []
for p in feat_raw:
    a = get_alt(p)
    t = get_title(p)
    fname = p.split('/')[-1]
    if not a:
        a = fname.replace('-', ' ').replace('_', ' ').replace('.jpg', '').replace('.png', '').title()
    feat_data.append({'p': '/' + p, 'a': a, 't': t, 'd': ''})
    print(f'  {fname[:50]}')
    print(f'    a: {a[:60]}')
    print(f'    t: {t[:60]}')

# Specs
print('\n--- Specs ---')
specs_raw = re.findall(
    r'c-compare-selling__spec-name"><p>(.*?)</p>.*?c-compare-selling__spec-desc"><p>(.*?)</p>',
    html, re.DOTALL)
specs = {}
for k, v in specs_raw:
    k2 = re.sub(r'<[^>]+>', '', k).strip()
    v2 = re.sub(r'<[^>]+>', '', v).strip()
    if k2 and v2:
        k2 = re.sub(r'[^\w]', '_', k2).strip('_')
        specs[k2] = v2
print(f'Specs: {len(specs)}')
for k, v in list(specs.items())[:10]:
    print(f'  {k}: {v}')

# Save
data = {'nm': nm, 'pr': pr_val, 'gal': gal_data, 'feat': feat_data, 'sp': specs}
out = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/32u721sa_data.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'\nSaved: gal={len(gal_data)}, feat={len(feat_data)}, sp={len(specs)}')
