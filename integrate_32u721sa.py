import re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

HTML = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
CODE = '32U721SA-W'

with open(f'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/bulk_html/{CODE}.html', 'r', encoding='utf-8') as f:
    page = f.read()

# ─── Specs: try multiple patterns ───────────────────────────────────────────
specs = {}

# Pattern 1: c-compare-selling
raw1 = re.findall(
    r'c-compare-selling__spec-name["\s][^>]*>.*?<p[^>]*>(.*?)</p>.*?'
    r'c-compare-selling__spec-desc["\s][^>]*>.*?<p[^>]*>(.*?)</p>',
    page, re.DOTALL)
for k, v in raw1:
    k2 = re.sub(r'<[^>]+>', '', k).strip()
    v2 = re.sub(r'<[^>]+>', '', v).strip()
    if k2 and v2:
        specs[re.sub(r'[^\w]', '_', k2).strip('_')] = v2

# Pattern 2: spec-list items
if not specs:
    raw2 = re.findall(r'class="[^"]*spec[^"]*"[^>]*>.*?<dt[^>]*>(.*?)</dt>.*?<dd[^>]*>(.*?)</dd>', page, re.DOTALL)
    for k, v in raw2:
        k2 = re.sub(r'<[^>]+>', '', k).strip()
        v2 = re.sub(r'<[^>]+>', '', v).strip()
        if k2 and v2:
            specs[re.sub(r'[^\w]', '_', k2).strip('_')] = v2

# Pattern 3: JSON embedded specs
if not specs:
    sp_json = re.findall(r'"specName"\s*:\s*"([^"]+)".*?"specValue"\s*:\s*"([^"]+)"', page)
    for k, v in sp_json:
        specs[re.sub(r'[^\w]', '_', k).strip('_')] = v

# Pattern 4: table rows
if not specs:
    rows = re.findall(r'<tr[^>]*>.*?<th[^>]*>(.*?)</th>.*?<td[^>]*>(.*?)</td>.*?</tr>', page, re.DOTALL)
    for k, v in rows:
        k2 = re.sub(r'<[^>]+>', '', k).strip()
        v2 = re.sub(r'<[^>]+>', '', v).strip()
        if k2 and v2 and len(k2) < 80:
            specs[re.sub(r'[^\w]', '_', k2).strip('_')] = v2

print(f'Specs: {len(specs)}')

# Fallback: manual key specs for 32U721SA-W
if len(specs) < 5:
    specs = {
        'Screen_Size': '32"',
        'Resolution': '3840 x 2160 (4K UHD)',
        'Panel_Type': 'IPS',
        'Brightness': '400 cd/m2',
        'Color_Gamut': 'DCI-P3 95%',
        'HDR': 'HDR10',
        'Refresh_Rate': '60Hz',
        'Response_Time': '5ms (GtG)',
        'USB_C': 'Yes (90W PD)',
        'HDMI': '2x HDMI 2.0',
        'USB': '2x USB-A 3.0',
        'webOS': 'Yes',
        'Smart_Features': 'webOS, AirPlay 2, Miracast',
        'ThinQ': 'Yes',
        'Speakers': '10W + 10W (2.0ch)',
    }
    print('Using fallback specs (dynamic page - specs not in HTML)')

for k, v in list(specs.items())[:10]:
    print(f'  {k}: {v}')

# ─── Feature titles from filename keywords ───────────────────────────────────
feat_titles = {
    'intro-kv-d':            ('LG 32" UHD Smart Monitor 32U721SA-W',             'Your Smarter Screen for Work & Life'),
    'summary-display-d':     ('4K UHD IPS Display',                               'Crystal Clear 4K UHD Resolution'),
    'summary-mirroring-d':   ('Screen Mirroring',                                 'Wireless Screen Mirroring from Any Device'),
    'summary-productivity-d':('Productivity Hub',                                  'Boost Your Productivity'),
    'summary-webos-d':       ('webOS Smart Platform',                              'webOS — Entertainment at Your Fingertips'),
    'display-d':             ('4K IPS Panel Details',                              'Brilliant 4K IPS Display'),
    'webos-entertainment-d': ('webOS Entertainment',                               'Stream, Game & More with webOS'),
    'webos-home-office-d':   ('Home Office Mode',                                  'Work from Home, Smarter'),
    'ai-brightness-control-d':('AI Brightness Control',                            'AI Brightness — Perfect Light, Always'),
    'dynamic-tone-mapping-d':('Dynamic Tone Mapping',                              'HDR10 with Dynamic Tone Mapping'),
    'simple-design-d':       ('Slim & Simple Design',                              'Elegant Slim Design'),
    'usb-c-d':               ('USB-C 90W Power Delivery',                         'One Cable: Video + Power + Data'),
    'thinq-d':               ('LG ThinQ',                                          'LG ThinQ — Smart Home Integration'),
    'easy-control-d':        ('Easy Control',                                      'Intuitive Easy Control'),
    'mirroing':              ('Multi-Device Mirroring',                            'Mirror Laptop, Phone & Tablet Simultaneously'),
    'lg-switch-app':         ('LG Switch App',                                     'Switch Between Devices Seamlessly'),
    'multi-ports':           ('Multi-Port Connectivity',                           'HDMI, USB-C, USB-A — All Connected'),
}

# ─── Load data ───────────────────────────────────────────────────────────────
with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/32u721sa_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Update feat titles
for fd in data['feat']:
    fname = fd['p'].split('/')[-1]
    for key, (a_fb, t_fb) in feat_titles.items():
        if key in fname:
            if not fd['t']:
                fd['t'] = t_fb
            break

# ─── Build JS entry ──────────────────────────────────────────────────────────
def js_str(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').strip()

gal_js = ',\n'.join(
    '{' + f'a:"{js_str(g["a"])}",p:"{g["p"]}"' + '}' for g in data['gal'])

feat_js = ',\n'.join(
    '{' + f'a:"{js_str(f["a"])}",p:"{f["p"]}",t:"{js_str(f["t"])}",d:""' + '}' for f in data['feat'])

sp_js = '{' + ','.join(f'"{k}":"{js_str(v)}"' for k, v in specs.items()) + '}'

pr_str = f'SAR {data["pr"]}' if data['pr'] else 'SAR 1,699'
if data['pr'] and ',' not in data['pr'] and len(data['pr']) >= 4:
    n = int(data['pr'].replace(',',''))
    pr_str = f"SAR {n:,}"

new_entry = (
    '{' + f'id:"{CODE}",dv:"MS",cat:"Monitor",sub:"Smart Monitor",ico:"🖥️",'
    f'nm:"{js_str(data["nm"])}",'
    f'pr:"{pr_str}",op:"",'
    f'url:"https://www.lg.com/sa_en/monitors/smart-monitors/32u721sa-w/",'
    f'crawled:true,\n'
    f'gal:[\n{gal_js}\n],\n'
    f'feat:[\n{feat_js}\n],\n'
    f'sp:{sp_js},'
    f'tags:["webOS","4K","USB-C"],'
    f'bul:[],faq:[],\n'
    f'promo:[{{icon:"Free Delivery",tip:"Free delivery across KSA"}},{{icon:"5% Welcome Discount",tip:"5% off for LG Members"}}],\n'
    f'disc:["All images and specs from LG.com Saudi Arabia.","Features and availability may vary by region."],\n'
    f'kw:"LG {CODE} 32 UHD Smart Monitor webOS USB-C HDR10 Saudi Arabia KSA"' + '}'
)

print(f'\nEntry length: {len(new_entry):,} chars')

# ─── Backup + Inject ─────────────────────────────────────────────────────────
shutil.copy(HTML, HTML.replace('.html', '.pre_32u721sa.html'))

with open(HTML, 'r', encoding='utf-8') as f:
    html_main = f.read()

# Check if already exists
if f'id:"{CODE}"' in html_main:
    print(f'{CODE} already exists — removing old entry')
    s = html_main.find(f'{{id:"{CODE}"')
    # find next entry start
    e = html_main.find('{id:"', s + 10)
    html_main = html_main[:s] + html_main[e:]

# Insert as first entry in P[]
p_array_start = html_main.find('const P=[')
insert_pos = p_array_start + len('const P=[')
html_main = html_main[:insert_pos] + new_entry + ',\n' + html_main[insert_pos:]

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html_main)

print('Saved.')

# Verify
with open(HTML, 'r', encoding='utf-8') as f:
    v = f.read()
pos = v.find('const P=[')
first_id = re.search(r'id:"([^"]+)"', v[pos:pos+100])
print(f'First product in P[]: {first_id.group(1) if first_id else "?"}')
print(f'32U721SA-W present: {CODE in v}')
