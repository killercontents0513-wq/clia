"""Integrate deep_data into v6_18 with dimensions and deduplication.

Each gallery/feature entry gets w/h embedded so the A+ generator can choose
module by aspect ratio. Gallery de-duplicated to one best variant per view.
"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
HTML = f'{BASE}/LG_AI_Content_Hub_v6_18.html'

with open(f'{BASE}/deep_data.json','r',encoding='utf-8') as f: DATA=json.load(f)

def jsstr(s):
    if s is None: s=''
    s = str(s)
    s = (s.replace('\u201c','"').replace('\u201d','"')
         .replace('\u2018',"'").replace('\u2019',"'"))
    s = s.replace('\\','\\\\').replace('"','\\"')
    s = s.replace('\n',' ').replace('\r','').replace('\t',' ')
    return re.sub(r'\s+',' ', s).strip()

def format_price(v):
    if not v: return ''
    try:
        f=float(v)
        return f'SAR {int(f):,}' if f==int(f) else f'SAR {f:,.2f}'
    except: return f'SAR {v}'

def dedup_gallery(items):
    """Keep best variant per unique 'view position'.
    Priority: basic-large > 2010 > zoom (DZ) > gallery-NN > D-NN > thumbnail
    Group key: extract position number or unique label from filename.
    """
    def rank(nm):
        n = nm.lower()
        if 'basic-large' in n: return 1
        if 'basic_large' in n: return 1
        if '2010' in n: return 2
        if re.match(r'^dz[-_]', n) or 'zoom' in n: return 3
        if re.match(r'^d[-_]\d', n): return 4
        if 'gallery-' in n: return 5
        if 'basic' in n and '450' in n: return 6
        if '450' in n: return 7
        if re.match(r'^s[-_]\d', n): return 8
        if 'mobilezoom' in n or 'mz' in n: return 9
        if 'thumbnail' in n: return 10
        return 11
    def pos_key(nm):
        n = nm.lower()
        # extract the "position number" like 01, 02, etc.
        m = re.search(r'(?:dz|mz|d|s|z|l|gallery|thumbnail|mobilezoom)[-_]?(\d{1,2})', n)
        if m: return m.group(1).lstrip('0') or '0'
        m = re.search(r'-(\d{1,2})[-_.]', n)
        if m: return m.group(1).lstrip('0') or '0'
        m = re.search(r'(\d{1,2})', n)
        return m.group(1).lstrip('0') if m else n
    # Group by position, pick best
    by_pos = {}
    for it in items:
        nm = it['p'].split('/')[-1]
        key = pos_key(nm)
        r = rank(nm)
        if key not in by_pos or r < by_pos[key][0]:
            by_pos[key] = (r, it)
    # Sort by position number (numeric)
    def sort_key(kv):
        k = kv[0]
        try: return (0, int(k))
        except: return (1, k)
    return [v[1] for k, v in sorted(by_pos.items(), key=sort_key)]

def format_entry(d):
    code = d['code']
    name = jsstr(d['name'])
    price = format_price(d['price'])
    msrp = format_price(d['msrp'])
    cat, sub, ico, dv, url = d['cat'], d['sub'], d['ico'], d['dv'], d['url']

    # Gallery dedup, max 16
    gallery = dedup_gallery(d['gallery'])[:16]
    feats = d['features'][:18]

    # Format arrays with w/h
    gal_items = []
    for g in gallery:
        a = jsstr(g['a']); p = jsstr(g['p'])
        w = int(g.get('w',0) or 0); h = int(g.get('h',0) or 0)
        gal_items.append(f'{{a:"{a}",p:"{p}",w:{w},h:{h}}}')
    gal = '[\n' + ',\n'.join(gal_items) + '\n]' if gal_items else '[]'

    feat_items = []
    for ft in feats:
        a = jsstr(ft['a']); p = jsstr(ft['p'])
        t = jsstr(ft['t']); dd = jsstr(ft.get('d',''))
        w = int(ft.get('w',0) or 0); h = int(ft.get('h',0) or 0)
        feat_items.append(f'{{a:"{a}",p:"{p}",t:"{t}",d:"{dd}",w:{w},h:{h}}}')
    feat = '[\n' + ',\n'.join(feat_items) + '\n]' if feat_items else '[]'

    # Specs: sanitize keys
    sp_items = []
    for k, v in (d.get('specs') or {}).items():
        key = re.sub(r'[^A-Za-z0-9]','_', k).strip('_')[:30]
        if not key: continue
        if key[0].isdigit(): key = 'K_' + key
        sp_items.append(f'"{key}":"{jsstr(v)}"')
    sp = '{' + ','.join(sp_items) + '}' if sp_items else '{}'

    # Tags
    blob = (name + ' ' + ' '.join((d.get('specs') or {}).values())).lower()
    tag_pats = ['4k','oled','miniled','qned','webos','dolby atmos','dolby vision','ai dd','ai',
                'thinq','inverter','smart inverter','steam','turbowash','ip67','ipx4','auracast',
                'bluetooth','usb-c','hdr10','144hz','480hz','wi-fi','allergy care','6 motion',
                'quadwash','truesteam','sensor dry','heat pump','side-by-side','multi door',
                'kompressor','swirl','a9']
    tags = []
    for tp in tag_pats:
        if tp in blob and tp.title() not in tags: tags.append(tp.title())
    if not tags: tags = [cat, sub]
    tags = tags[:8]
    tags_str = '[' + ','.join(f'"{jsstr(t)}"' for t in tags) + ']'

    # Bullets — pull from feature titles
    bul_items = []
    for ft in feats[:8]:
        tt = jsstr(ft.get('t','')).upper()
        dd = jsstr(ft.get('d',''))
        if tt and dd and dd != ft.get('t',''):
            bul_items.append(f'"{tt}: {dd[:140]}"')
        elif tt:
            bul_items.append(f'"{tt}"')
    if not bul_items:
        for k, v in list((d.get('specs') or {}).items())[:5]:
            bul_items.append(f'"{jsstr(k).upper()}: {jsstr(v)[:120]}"')
    bul = '[' + ','.join(bul_items) + ']' if bul_items else '[]'

    # FAQ — code + first feature
    faq_items = [f'{{q:"What is the model code?",a:"{code}"}}']
    for ft in feats[:2]:
        tq = jsstr(ft.get('t',''))
        ta = jsstr(ft.get('d',''))
        if tq and ta: faq_items.append(f'{{q:"About {tq}?",a:"{ta}"}}')
    faq = '[' + ','.join(faq_items) + ']'

    if dv == 'HA':
        promo = '[{icon:"Free Delivery",tip:"Free delivery across KSA"},{icon:"Free Installation",tip:"Free installation service"},{icon:"Easy Installment",tip:"Flexible installments via Tamara"},{icon:"Bank Offers",tip:"Extra savings with partner banks"},{icon:"5% Welcome Discount",tip:"5% off for LG Members"}]'
    else:
        promo = '[{icon:"Free Delivery",tip:"Free delivery across KSA"},{icon:"Easy Installment",tip:"Flexible installments via Tamara"},{icon:"Bank Offers",tip:"Extra savings with partner banks"},{icon:"5% Welcome Discount",tip:"5% off for LG Members"}]'
    disc = '["All images and specs from LG.com Saudi Arabia.","Features and availability may vary by region."]'
    kw = jsstr(f'LG {code} {name} {cat} {sub} Saudi Arabia KSA {" ".join(tags[:5])}')

    entry = (
        f'{{id:"{code}",dv:"{dv}",cat:"{cat}",sub:"{sub}",ico:"{ico}",'
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
    return entry

with open(HTML,'r',encoding='utf-8') as f: html=f.read()

updated = []
for d in DATA:
    code = d['code']
    entry = format_entry(d)
    # Find existing block by id
    pat = re.compile(r'\{id:"'+re.escape(code)+r'"')
    m = pat.search(html)
    if not m:
        print(f'MISS {code}')
        continue
    start = m.start()
    # Balance braces to find block end
    depth = 0
    i = start
    in_str = None
    while i < len(html):
        c = html[i]
        if in_str:
            if c == '\\': i += 2; continue
            if c == in_str: in_str = None
        else:
            if c in ('"', "'"): in_str = c
            elif c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        i += 1
    else:
        print(f'Unbalanced for {code}'); continue
    html = html[:start] + entry + html[end:]
    updated.append(code)
    print(f'U {code} — gal={d["gallery"] and "dedup" or "0"}, feat={len(d["features"])}, sp={len(d["specs"])}')

with open(HTML,'w',encoding='utf-8') as f: f.write(html)
print(f'\nUpdated {len(updated)} / {len(DATA)}')
