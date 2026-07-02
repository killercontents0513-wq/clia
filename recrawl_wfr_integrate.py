"""Integrate WFR1114WH ordered data into v6_18 - NO dedup, strict PDP order."""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
HTML = f'{BASE}/LG_AI_Content_Hub_v6_18.html'

with open(f'{BASE}/wfr_ordered.json','r',encoding='utf-8') as f: D=json.load(f)

def jsstr(s):
    if s is None: s=''
    s = str(s)
    s = (s.replace('\u201c','"').replace('\u201d','"')
         .replace('\u2018',"'").replace('\u2019',"'"))
    s = s.replace('\\','\\\\').replace('"','\\"')
    s = s.replace('\n',' ').replace('\r','').replace('\t',' ')
    return re.sub(r'\s+',' ', s).strip()

def price_fmt(v):
    if not v: return ''
    try:
        f=float(v)
        return f'SAR {int(f):,}' if f==int(f) else f'SAR {f:,.2f}'
    except: return f'SAR {v}'

code = D['code']
name = jsstr(D['name'])
price = price_fmt(D['price'])
msrp = price_fmt(D['msrp'])
url = D['url']

# Gallery: ALL items, in PDP order, with w/h
gal_items = []
for g in D['gallery']:
    a = jsstr(g['a']); p = jsstr(g['p'])
    w = int(g.get('w',0) or 0); h = int(g.get('h',0) or 0)
    gal_items.append(f'{{a:"{a}",p:"{p}",w:{w},h:{h}}}')
gal = '[\n' + ',\n'.join(gal_items) + '\n]'

# Features: ALL items, in PDP order, with w/h (desktop + mobile kept separate)
feat_items = []
for ft in D['features']:
    a = jsstr(ft['a']); p = jsstr(ft['p'])
    t = jsstr(ft['t']); dd = jsstr(ft.get('d',''))
    w = int(ft.get('w',0) or 0); h = int(ft.get('h',0) or 0)
    feat_items.append(f'{{a:"{a}",p:"{p}",t:"{t}",d:"{dd}",w:{w},h:{h}}}')
feat = '[\n' + ',\n'.join(feat_items) + '\n]'

# Specs
sp_items = []
for k, v in (D.get('specs') or {}).items():
    key = re.sub(r'[^A-Za-z0-9]','_', k).strip('_')[:30]
    if not key: continue
    if key[0].isdigit(): key = 'K_' + key
    sp_items.append(f'"{key}":"{jsstr(v)}"')
sp = '{' + ','.join(sp_items) + '}'

# Tags
blob = (name + ' ' + ' '.join((D.get('specs') or {}).values())).lower()
tag_pats = ['ai dd','ai','thinq','inverter','steam','turbowash','allergy care','6 motion',
            'wi-fi','front load','vivace','smart diagnosis','big capacity','11 kg']
tags = []
for tp in tag_pats:
    if tp in blob and tp.title() not in tags: tags.append(tp.title())
if not tags: tags=['Front Load','Washer']
tags_str = '[' + ','.join(f'"{jsstr(t)}"' for t in tags[:8]) + ']'

# Bullets from feature titles (dedup by title)
seen_t = set()
bul_items = []
for ft in D['features']:
    tt = ft.get('t','')
    if tt and tt not in seen_t and 'Wm Vivace' not in tt and 'Wd Vivace' not in tt:
        seen_t.add(tt)
        dd = jsstr(ft.get('d',''))
        tu = jsstr(tt).upper()
        if dd and dd != tt:
            bul_items.append(f'"{tu}: {dd[:140]}"')
        else:
            bul_items.append(f'"{tu}"')
        if len(bul_items) >= 8: break
bul = '[' + ','.join(bul_items) + ']'

# FAQ
faq_items = [f'{{q:"What is the model code?",a:"{code}"}}']
for ft in D['features'][:3]:
    tq = jsstr(ft.get('t',''))
    ta = jsstr(ft.get('d',''))
    if tq and ta and 'Vivace' not in tq:
        faq_items.append(f'{{q:"About {tq}?",a:"{ta}"}}')
faq = '[' + ','.join(faq_items[:4]) + ']'

promo = '[{icon:"Free Delivery",tip:"Free delivery across KSA"},{icon:"Free Installation",tip:"Free installation service"},{icon:"Easy Installment",tip:"Flexible installments via Tamara"},{icon:"Bank Offers",tip:"Extra savings with partner banks"},{icon:"5% Welcome Discount",tip:"5% off for LG Members"}]'
disc = '["All images and specs from LG.com Saudi Arabia.","Features and availability may vary by region."]'
kw = jsstr(f'LG {code} {name} Washer Front Load Saudi Arabia KSA AI DD Steam TurboWash')

entry = (
    f'{{id:"{code}",dv:"HA",cat:"Washer",sub:"Front Load",ico:"🧺",'
    f'nm:"{name}",pr:"{price}",op:"{msrp}",url:"{url}",crawled:true,\n'
    f'gal:{gal},\n'
    f'feat:{feat},\n'
    f'sp:{sp},tags:{tags_str},\n'
    f'bul:{bul},\n'
    f'faq:{faq},\n'
    f'promo:{promo},\n'
    f'disc:{disc},\n'
    f'kw:"{kw}"}}'
)

# Find + replace
with open(HTML,'r',encoding='utf-8') as f: html=f.read()
m = re.search(r'\{id:"'+re.escape(code)+r'"', html)
if not m:
    raise SystemExit('Entry not found')
start = m.start()
depth=0; i=start; in_str=None
while i < len(html):
    c = html[i]
    if in_str:
        if c == '\\': i += 2; continue
        if c == in_str: in_str = None
    else:
        if c == '"' or c == "'": in_str = c
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end = i+1
                break
    i += 1
print(f'Replacing block {start}..{end} ({end-start} chars) with {len(entry)} chars')
html = html[:start] + entry + html[end:]
with open(HTML,'w',encoding='utf-8') as f: f.write(html)
print(f'Entry: gal={len(D["gallery"])}, feat={len(D["features"])}, specs={len(D["specs"])}')
