"""
Final fix for RH81T2SP7RM:
- Base: Apr21 entry (keeps ico, op, amz_title, amz_desc, bul, faq, promo, disc, kw)
- Gallery: DZ-01→15 in correct order with actual dims (2010x1334)
- Features: composite structure (1 single intro + 2-image pair + 3-image trio)
- Written DIRECTLY to HTML — does NOT go through bulk_integrate.py
"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'

def extract_entry(html, code):
    idx = html.find(f'id:"{code}"')
    start = html.rfind('{', 0, idx)
    depth=0; i=start
    while i < len(html):
        if html[i]=='{': depth+=1
        elif html[i]=='}':
            depth-=1
            if depth==0: break
        i+=1
    return html[start:i+1], start, i+1

# ── Load files ────────────────────────────────────────────────────────────────
with open(f'{BASE}/LG_AI_Content_Hub_v6_18.pre_65QNED93A6A.html','r',encoding='utf-8',errors='replace') as f:
    apr21 = f.read()
with open(f'{BASE}/LG_AI_Content_Hub_v6_18.html','r',encoding='utf-8',errors='replace') as f:
    current = f.read()

# ── Extract Apr21 base entry ──────────────────────────────────────────────────
base_entry, _, _ = extract_entry(apr21, 'RH81T2SP7RM')
print(f'Apr21 base entry: {len(base_entry)} chars')

# ── Build corrected gallery (DZ-01 → DZ-15, 2010x1334) ───────────────────────
gallery_alts = {
    'DZ-01': 'Front view',
    'DZ-02': 'Front Open view',
    'DZ-03': 'Knob Panel Detail',
    'DZ-04': 'Drum detail',
    'DZ-05': 'Drum',
    'DZ-06': 'Drawer view',
    'DZ-07': 'Detail View',
    'DZ-08': 'Top Left Perspective',
    'DZ-09': 'Top Perspective',
    'DZ-10': 'Detail View',
    'DZ-11': 'Left side view',
    'DZ-12': 'Left Side Open',
    'DZ-13': 'Right Side View',
    'DZ-14': 'Side view',
    'DZ-15': 'Back view',
}
gal_items = []
for i in range(1, 16):
    key = f'DZ-{str(i).zfill(2)}'
    alt = gallery_alts.get(key, f'View {i}')
    gal_items.append(f'{{a:"{alt}",p:"/images/dryers/RH81T2SP7RM/{key}.jpg",w:2010,h:1334}}')
gal_js = '[' + ','.join(gal_items) + ']'

# ── Build composite features ─────────────────────────────────────────────────
feat_js = '''[
{a:"There is a dryer on the background of a smiling mother and daughter.",p:"/images/wm/features/dryer-vestel-odm-dryer-white-01-intro-d.jpg",t:"LG Heat Pump Dryer for Sustainable Care",d:"*Product images are for illustrative purpose only and may differ from actual product.",w:1600,h:1450},
{a:"Heater Dryer vs Heat Pump",p:"/images/wm/features/dryer-vestel-odm-dryer-white-02-2-1-heater-dryer-d.jpg",t:"Enjoy the Gentle Dry with Heat Pump",d:"*It may vary depending on the texture of the clothes.",w:800,h:700,imgs:[{a:"Heater Dryer",p:"/images/wm/features/dryer-vestel-odm-dryer-white-02-2-1-heater-dryer-d.jpg",w:800,h:700},{a:"Heat Pump Dryer",p:"/images/wm/features/dryer-vestel-odm-dryer-white-02-2-2-heatpump-dryer-d.jpg",w:800,h:700}]},
{a:"Visible and Elegant Design",p:"/images/wm/features/dryer-vestel-odm-dryer-white-05-2-1-washer-and-dryer-d.jpg",t:"Visible and Elegant Design",d:"Stylish design fits seamlessly into modern home interiors.",w:521,h:750,imgs:[{a:"Washer and Dryer",p:"/images/wm/features/dryer-vestel-odm-dryer-white-05-2-1-washer-and-dryer-d.jpg",w:521,h:750},{a:"Door Detail",p:"/images/wm/features/dryer-vestel-odm-dryer-white-05-2-2-door-d.jpg",w:739,h:363},{a:"Control Panel",p:"/images/wm/features/dryer-vestel-odm-dryer-white-05-2-3-control-panel-d.jpg",w:739,h:363}]}
]'''

# ── Replace gal and feat in base entry ───────────────────────────────────────
# Replace gal:[...] block
new_entry = re.sub(r'gal:\[.*?\](?=,feat:)', f'gal:{gal_js}', base_entry, flags=re.DOTALL)
# Replace feat:[...] block
new_entry = re.sub(r'feat:\[.*?\](?=,sp:)', f'feat:{feat_js}', new_entry, flags=re.DOTALL)

print(f'New entry: {len(new_entry)} chars')

# Verify
gal_count = new_entry.count('DZ-')
feat_count = new_entry.count('dryer-vestel-odm')
print(f'Gallery DZ refs: {gal_count}')
print(f'Feature refs: {feat_count}')
print(f'ico: {"🌀" if "ico:\"🌀\"" in new_entry else "WRONG"}')
print(f'op: {"✓" if "SAR 6,499" in new_entry else "MISSING"}')
print(f'amz_title: {"✓" if "amz_title" in new_entry else "MISSING"}')
print(f'imgs composite: {"✓" if "imgs:[" in new_entry else "MISSING"}')

# ── Write to HTML ─────────────────────────────────────────────────────────────
_, cur_start, cur_end = extract_entry(current, 'RH81T2SP7RM')
new_html = current[:cur_start] + new_entry + current[cur_end:]

with open(f'{BASE}/LG_AI_Content_Hub_v6_18.html','w',encoding='utf-8') as f:
    f.write(new_html)

print(f'\nHTML: {len(current):,} → {len(new_html):,} bytes')
print('Done. RH81T2SP7RM fully restored with composite features.')
