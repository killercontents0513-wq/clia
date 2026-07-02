"""Patch WFR1114WH feature labels/titles: replace filename-fallback with
smart-derived labels + try harder backward HTML search for real titles."""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
HTML = f'{BASE}/LG_AI_Content_Hub_v6_18.html'

with open(f'{BASE}/deep_html/WFR1114WH.html','r',encoding='utf-8',errors='replace') as f:
    pdp = f.read()
with open(f'{BASE}/wfr_ordered.json','r',encoding='utf-8') as f:
    D = json.load(f)

LABEL_FIXES = {
    'Thinq': 'ThinQ',
    'Aidd Info': 'AI DD Info',
    'Aidd': 'AI DD',
    'Smartthinq': 'Smart ThinQ',
    'Turbowash': 'TurboWash',
    'Druability': 'Durability',
    'Smart Thinq': 'Smart ThinQ',
}

def smart_title(nm):
    base = nm.rsplit('.',1)[0]
    base = re.sub(r'^(?:WD|WM|wd|wm)-[a-zA-Z0-9]+-V\d+-[a-zA-Z0-9]+-[a-zA-Z0-9]+-', '', base)
    base = re.sub(r'[-_](?:Desktop|Mobile|desktop|mobile|d|m)(?:[-_]\w+)?$', '', base)
    base = re.sub(r'_t\d+$', '', base)
    base = re.sub(r'^\d+[-_]\d*[-_]*', '', base)
    # Handle WFR-specific saso-d pattern
    base = re.sub(r'^WFR\d+[A-Z]*-', '', base, flags=re.I)
    label = base.replace('-',' ').replace('_',' ').strip()
    label = re.sub(r'\s+',' ',label).strip().title()
    # Apply known fixes
    for k,v in LABEL_FIXES.items():
        label = label.replace(k, v)
    return label or 'Feature'

def clean(s):
    s = re.sub(r'<[^>]+>','', s or '')
    s = (s.replace('&#x27;',"'").replace('&amp;','&').replace('&quot;','"')
         .replace('&lt;','<').replace('&gt;','>').replace('&nbsp;',' ')
         .replace('\u201c','"').replace('\u201d','"').replace('\u2018',"'").replace('\u2019',"'"))
    return re.sub(r'\s+',' ',s).strip()

# Walk through features — keep the existing t/d if they exist and are real,
# else replace with smart_title derived from filename
BAD_TITLES = ['Wd Vivace V900 Vc2 Blacks','Wm Vivace V700 Vc3 White','Wd Vivace','Wm Vivace']

def is_bad(title):
    if not title: return True
    for b in BAD_TITLES:
        if b.lower() in title.lower(): return True
    return False

# For 'saso' (summary) images, use "Summary" label
for ft in D['features']:
    nm = ft['p'].split('/')[-1]
    # If title is bad fallback, replace
    if is_bad(ft.get('t','')):
        if 'saso' in nm.lower():
            ft['t'] = 'Product Summary'
        else:
            ft['t'] = smart_title(nm)
    # Always regenerate alt label (shorter version)
    if is_bad(ft.get('a','')):
        ft['a'] = smart_title(nm)[:25] or 'Feature'

# Write back to JSON first
with open(f'{BASE}/wfr_ordered.json','w',encoding='utf-8') as f:
    json.dump(D, f, ensure_ascii=False, indent=1)

# Then rebuild and re-integrate the entry
def jsstr(s):
    if s is None: s=''
    s = str(s)
    s = (s.replace('\u201c','"').replace('\u201d','"').replace('\u2018',"'").replace('\u2019',"'"))
    s = s.replace('\\','\\\\').replace('"','\\"')
    s = s.replace('\n',' ').replace('\r','').replace('\t',' ')
    return re.sub(r'\s+',' ', s).strip()

def price_fmt(v):
    if not v: return ''
    try:
        f=float(v)
        return f'SAR {int(f):,}' if f==int(f) else f'SAR {f:,.2f}'
    except: return f'SAR {v}'

code=D['code']; name=jsstr(D['name']); price=price_fmt(D['price']); msrp=price_fmt(D['msrp']); url=D['url']

gal_items=[]
for g in D['gallery']:
    a=jsstr(g['a']); p=jsstr(g['p']); w=int(g.get('w',0) or 0); h=int(g.get('h',0) or 0)
    gal_items.append(f'{{a:"{a}",p:"{p}",w:{w},h:{h}}}')
gal='[\n' + ',\n'.join(gal_items) + '\n]'

feat_items=[]
for ft in D['features']:
    a=jsstr(ft['a']); p=jsstr(ft['p']); t=jsstr(ft['t']); dd=jsstr(ft.get('d',''))
    w=int(ft.get('w',0) or 0); h=int(ft.get('h',0) or 0)
    feat_items.append(f'{{a:"{a}",p:"{p}",t:"{t}",d:"{dd}",w:{w},h:{h}}}')
feat='[\n' + ',\n'.join(feat_items) + '\n]'

sp_items=[]
for k,v in (D.get('specs') or {}).items():
    key=re.sub(r'[^A-Za-z0-9]','_',k).strip('_')[:30]
    if not key: continue
    if key[0].isdigit(): key='K_'+key
    sp_items.append(f'"{key}":"{jsstr(v)}"')
sp='{' + ','.join(sp_items) + '}'

blob=(name+' '+' '.join((D.get('specs') or {}).values())).lower()
tag_pats=['ai dd','ai','thinq','inverter','steam','turbowash','allergy care','6 motion','wi-fi','front load','vivace','smart diagnosis','11 kg']
tags=[]
for tp in tag_pats:
    if tp in blob and tp.title() not in tags: tags.append(tp.title())
if not tags: tags=['Front Load','Washer']
tags_str='[' + ','.join(f'"{jsstr(t)}"' for t in tags[:8]) + ']'

seen_t=set(); bul_items=[]
for ft in D['features']:
    tt=ft.get('t','')
    if tt and tt not in seen_t and not any(x in tt for x in BAD_TITLES):
        seen_t.add(tt)
        dd=jsstr(ft.get('d','')); tu=jsstr(tt).upper()
        if dd and dd != tt: bul_items.append(f'"{tu}: {dd[:140]}"')
        else: bul_items.append(f'"{tu}"')
        if len(bul_items)>=8: break
bul='[' + ','.join(bul_items) + ']'

faq_items=[f'{{q:"What is the model code?",a:"{code}"}}']
for ft in D['features'][:3]:
    tq=jsstr(ft.get('t','')); ta=jsstr(ft.get('d',''))
    if tq and ta and not any(x in tq for x in BAD_TITLES):
        faq_items.append(f'{{q:"About {tq}?",a:"{ta}"}}')
faq='[' + ','.join(faq_items[:4]) + ']'

promo='[{icon:"Free Delivery",tip:"Free delivery across KSA"},{icon:"Free Installation",tip:"Free installation service"},{icon:"Easy Installment",tip:"Flexible installments via Tamara"},{icon:"Bank Offers",tip:"Extra savings with partner banks"},{icon:"5% Welcome Discount",tip:"5% off for LG Members"}]'
disc='["All images and specs from LG.com Saudi Arabia.","Features and availability may vary by region."]'
kw=jsstr(f'LG {code} {name} Washer Front Load Saudi Arabia KSA AI DD Steam TurboWash')

entry=(
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

with open(HTML,'r',encoding='utf-8') as f: html=f.read()
m=re.search(r'\{id:"'+re.escape(code)+r'"', html)
start=m.start()
depth=0; i=start; in_str=None
while i<len(html):
    c=html[i]
    if in_str:
        if c=='\\': i+=2; continue
        if c==in_str: in_str=None
    else:
        if c=='"' or c=="'": in_str=c
        elif c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: end=i+1; break
    i+=1
html=html[:start]+entry+html[end:]
with open(HTML,'w',encoding='utf-8') as f: f.write(html)
print('Updated feature labels/titles + integrated.')

# Preview new labels
for i, ft in enumerate(D['features']):
    print(f'  {i+1:2d}. t="{ft["t"][:50]:50s}"  a="{ft["a"]}"')
