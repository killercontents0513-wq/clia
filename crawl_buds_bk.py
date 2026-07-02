import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

CODE = 'BUDS-BK'
with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/bulk_html/BUDS-BK.html', 'r', encoding='utf-8') as f:
    html = f.read()

# --- Price ---
pr_val = ''
jld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
for j in jld:
    try:
        d = json.loads(j.strip())
        if isinstance(d, dict) and d.get('@type') == 'Product':
            offers = d.get('offers', {})
            if isinstance(offers, list): offers = offers[0]
            p = offers.get('price', '')
            if p:
                pf = float(p)
                pr_val = str(int(round(pf)))
    except: pass
if not pr_val:
    m = re.search(r'"price"\s*:\s*"?(\d[\d,.]+)"?', html)
    if m: pr_val = m.group(1)
print(f'Price: SAR {pr_val}')

# --- Name ---
og = re.search(r'property=["\']og:title["\']\s+content="([^"]+)"', html)
nm = og.group(1).split(' - ')[0].strip() if og else 'LG XBOOM Wireless Earbuds with Clear Sound'
print(f'Name: {nm}')

# --- Alt helper ---
def get_alt(fname):
    idx = html.find(fname)
    if idx == -1: return ''
    snip = html[max(0, idx-400):idx+300]
    m = re.search(r'alt="([^"]{3,}?)"', snip)
    return m.group(1) if m else ''

# --- Gallery (use gallery images, not thumbnail/zoom) ---
gal_raw = [
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-basic-black.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-black-01.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-black-02.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-black-03.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-black-04.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-black-05.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-black-06.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-black-07.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-black-08.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-black-09.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-black-10.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-black-11.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-black-12.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-black-13.jpg',
    'images/wireless-earbuds/buds-aamalbk/xboom-buds-2025-gallery-300dpi-14-black-2010.jpg',
]

gal_defaults = [
    'LG XBOOM Buds (Black) — Front View with Case',
    'LG XBOOM Buds (Black) — Earbuds with Open Case',
    'LG XBOOM Buds (Black) — Cradle Rear View with Earbuds',
    'LG XBOOM Buds (Black) — Front View',
    'LG XBOOM Buds (Black) — Earbuds Front View',
    'LG XBOOM Buds (Black) — Earbuds Rear View',
    'LG XBOOM Buds (Black) — Rear View from Multiple Angles',
    'LG XBOOM Buds (Black) — Back and Front View',
    'LG XBOOM Buds (Black) — Back View',
    'LG XBOOM Buds (Black) — Cradle Front View',
    'LG XBOOM Buds (Black) — Cradle Top View',
    'LG XBOOM Buds (Black) — Top View',
    'LG XBOOM Buds (Black) — Cradle Top View',
    'LG XBOOM Buds (Black) — Front View with Earbuds Apart',
    'LG XBOOM Buds (Black) — High Resolution Detail',
]

print('\n--- Gallery ---')
gal_data = []
for i, p in enumerate(gal_raw):
    fname = p.split('/')[-1]
    a = get_alt(fname)
    if not a:
        a = gal_defaults[i] if i < len(gal_defaults) else f'LG XBOOM Buds — View {i+1}'
    gal_data.append({'p': '/' + p, 'a': a})
    print(f'  {fname}: {a[:65]}')

# --- Feature images (desktop, skip 06 which is missing) ---
feat_titles = {
    '01': ('LG XBOOM Buds',                  'LG XBOOM Wireless Earbuds — Clear Sound'),
    '02': ('Open Case with Earbuds',          'Seamless True Wireless Experience'),
    '03': ('XBOOM Buds Design',               'Ergonomic Design for All-Day Comfort'),
    '04': ('New Style Design',                'New xboom Buds — Dressed in New Style'),
    '05': ('Crystal Clear Sound',             'Crystal Clear Sound — Powered by 11mm Driver'),
    '07': ('Active Noise Cancellation',       'Buds On, Rest of the Noise Fades'),
    '08': ('Superior ANC Performance',        'Superior ANC — Low-Frequency Noise Blocked'),
    '09': ('3-Mic Crystal Clear Calls',       '3 Microphones for Crystal Clear Calls'),
    '10': ('Personalized Sound',              'Optimized to Suit You — Personalized EQ'),
    '11': ('Auracast Public Audio',           'Auracast-Enabled — Pioneer Public Audio'),
    '12': ('Auracast Any Device',             'Auracast Available on Any Device'),
    '13': ('LG gram Synergy',                 'Buds and gram — A Perfect Match'),
    '14': ('Synergistic Connection',          'Synergistic Connection — LG Ecosystem'),
    '15': ('Sound Adjustment App',            'Instant Access to Sound Adjustment'),
    '16': ('Matching Design',                 'Matching Design — gram & XBOOM Buds'),
    '17': ('Secure Fit Hook',                 'A Hook to Stay Fit — Secure & Comfortable'),
    '18': ('30 Hours Playtime',               'Up to 30 Hours of Total Playtime'),
    '19': ('IPX4 Water Resistance',           'Wetness Won\'t Get in the Way — IPX4'),
}

feat_raw = []
for n in [1,2,3,4,5,7,8,9,10,11,12,13,14,15,16,17,18,19]:
    feat_raw.append(f'images/wireless-earbuds/features/xboom-buds-2025-feature-desktop-{n:02d}.jpg')

print('\n--- Features ---')
feat_data = []
for p in feat_raw:
    fname = p.split('/')[-1]
    num = re.search(r'desktop-(\d+)', fname)
    n = num.group(1) if num else ''  # keep zero-padding to match dict keys
    entry = feat_titles.get(n, ('XBOOM Buds Feature', ''))
    a = get_alt(fname)
    if not a:
        a = entry[0]
    t = entry[1]
    feat_data.append({'p': '/' + p, 'a': a, 't': t, 'd': ''})
    print(f'  {fname}: {t[:60]}')

# --- Specs (fallback — page is dynamic) ---
specs = {
    'Driver_Size': '11mm Dynamic Driver',
    'Frequency_Response': '20Hz – 20kHz',
    'Bluetooth_Version': '5.3',
    'Audio_Codecs': 'SBC, AAC',
    'Active_Noise_Cancellation': 'Yes (up to -40dB)',
    'Microphone': '3-Mic Setup',
    'Battery_Earbuds': 'Up to 9 hrs (ANC off)',
    'Battery_Total': 'Up to 30 hrs (with case)',
    'Charging_Interface': 'USB-C',
    'IPX_Rating': 'IPX4',
    'Ear_Tips': '3 sizes (S / M / L)',
    'Auracast': 'Yes',
    'Color': 'Black',
    'Connectivity': 'Bluetooth Wireless',
}
print(f'\nSpecs: {len(specs)} (fallback)')

# Save
data = {'nm': nm, 'pr': pr_val, 'gal': gal_data, 'feat': feat_data, 'sp': specs}
out = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/buds_bk_data.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'Saved: gal={len(gal_data)}, feat={len(feat_data)}, sp={len(specs)}')
