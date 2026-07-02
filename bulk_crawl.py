"""Bulk LG PDP crawler for v6_18 integration.
Downloads 42 PDPs in parallel, extracts images + features + specs, generates JS entries.
"""
import re, json, os, sys, io, urllib.request, urllib.parse, concurrent.futures as cf
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
os.makedirs(f'{BASE}/bulk_html', exist_ok=True)

# (id, category, sub, icon, dv, url) - category maps to v6_18 cat field
URLS = [
    ('LT19CBBSIN','Fridge','Top Freezer','🧊','HA','https://www.lg.com/sa_en/refrigerators/top-freezers/lt19cbbsin/'),
    ('WTT1410OL1','Washer','Twin Tub','🧺','HA','https://www.lg.com/sa_en/washing-machines/twin-tub/wtt1410ol1/'),
    ('WSN1508BMT','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wsn1508bmt/'),
    ('WFB0914XM','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wfb0914xm/'),
    ('WTV11BND','Washer','Top Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/top-load/wtv11bnd/'),
    ('WTV24HHP','Washer','Top Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/top-load/wtv24hhp/'),
    ('RH81T2SP7RM','Dryer','Heat Pump','🌀','HA','https://www.lg.com/sa_en/dryers/rh81t2sp7rm/'),
    ('A9LSLIM','Vacuum','Cordless','🧹','HA','https://www.lg.com/sa_en/vacuum-cleaners/a9lslim/'),
    ('WK1310BST','Washer','WashTower','🏢','HA','https://www.lg.com/sa_en/washing-machines/washtower/wk1310bst/'),
    ('RH10V9PV2W','Dryer','Heat Pump','🌀','HA','https://www.lg.com/sa_en/dryers/rh10v9pv2w/'),
    ('WFV1214BST1','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wfv1214bst1/'),
    ('65QNED93A6A','TV','QNED evo','📺','MS','https://www.lg.com/sa_en/tv-soundbars/qned/65qned93a6a/'),
    ('WTR22HHP','Washer','Top Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/top-load/wtr22hhp/'),
    ('WS2112BST','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/ws2112bst/'),
    ('WTT1108OW1','Washer','Twin Tub','🧺','HA','https://www.lg.com/sa_en/washing-machines/twin-tub/wtt1108ow1/'),
    ('WFN1510WHT','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wfn1510wht/'),
    ('S95TR','Audio','Soundbar','🔈','MS','https://www.lg.com/sa_en/tv-soundbars/soundbars/s95tr/'),
    ('RH18U8JVCW','Dryer','Heat Pump','🌀','HA','https://www.lg.com/sa_en/dryers/rh18u8jvcw/'),
    ('WSV0906XM','Washer','Combo','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load-combo/wsv0906xm/'),
    ('WFR1114WH','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wfr1114wh/'),
    ('A9K-SOLO','Vacuum','Cordless','🧹','HA','https://www.lg.com/sa_en/vacuum-cleaners/a9k-solo/'),
    ('LS19GBBDI','Fridge','Side-by-Side','🧊','HA','https://www.lg.com/sa_en/refrigerators/side-by-side/ls19gbbdi/'),
    ('WFR1114MB','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wfr1114mb/'),
    ('S20A','Audio','Soundbar','🔈','MS','https://www.lg.com/sa_en/speakers/soundbars/s20a/'),
    ('DFC435FW','Dish','Dishwasher','🍽️','HA','https://www.lg.com/sa_en/dishwashers/dfc435fw/'),
    ('S65TR','Audio','Soundbar','🔈','MS','https://www.lg.com/sa_en/tv-soundbars/soundbars/s65tr/'),
    ('WFN1310BST','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wfn1310bst/'),
    ('WFN1310WHT','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wfn1310wht/'),
    ('LS25CBBDIK','Fridge','Side-by-Side','🧊','HA','https://www.lg.com/sa_en/refrigerators/side-by-side/ls25cbbdik/'),
    ('WF0712MB','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wf0712mb/'),
    ('XG2TBK','Audio','Portable Speaker','🔊','MS','https://www.lg.com/sa_en/speakers/portable-speakers/xg2tbk/'),
    ('27US550-W','Monitor','UHD Monitor','🖥️','MS','https://www.lg.com/sa_en/monitors/uhd-4k-5k/27us550-w/'),
    ('WTV17HHD','Washer','Top Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/top-load/wtv17hhd/'),
    ('32GS95UV-B','Monitor','Gaming Monitor','🖥️','MS','https://www.lg.com/sa_en/monitors/gaming/32gs95uv-b/'),
    ('S45TR','Audio','Soundbar','🔈','MS','https://www.lg.com/sa_en/speakers/soundbars/s45tr/'),
    ('S80TR','Audio','Soundbar','🔈','MS','https://www.lg.com/sa_en/tv-soundbars/soundbars/s80tr/'),
    ('S90TR','Audio','Soundbar','🔈','MS','https://www.lg.com/sa_en/speakers/soundbars/s90tr/'),
    ('LT19HBHSIN','Fridge','Top Freezer','🧊','HA','https://www.lg.com/sa_en/refrigerators/top-freezers/lt19hbhsin/'),
    ('LSEL6333D','Cooking','Electric Cooker','🍳','HA','https://www.lg.com/sa_en/cooking-appliances/electric-cookers/lsel6333d/'),
    ('STAGE301','Audio','Speaker','🔊','MS','https://www.lg.com/sa_en/speakers/xboom/stage301/'),
    ('LM344VBNLF','Fridge','Multi-Door','🧊','HA','https://www.lg.com/sa_en/refrigerators/multi-doors/lm344vbnlf/'),
    ('WF2111BST','Washer','Front Load','🧺','HA','https://www.lg.com/sa_en/washing-machines/front-load/wf2111bst/'),
]

def fetch(item):
    code, cat, sub, ico, dv, url = item
    safe = code.replace('/','_')
    path = f'{BASE}/bulk_html/{safe}.html'
    if os.path.exists(path) and os.path.getsize(path) > 10000:
        return (code, path, True)
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        with open(path,'wb') as f: f.write(data)
        return (code, path, True)
    except Exception as e:
        print(f'FAIL {code}: {e}')
        return (code, path, False)

print(f'Fetching {len(URLS)} PDPs in parallel...')
with cf.ThreadPoolExecutor(max_workers=12) as ex:
    results = list(ex.map(fetch, URLS))
ok = sum(1 for _,_,s in results if s)
print(f'Fetched: {ok}/{len(URLS)}')

def clean_html(s):
    s = re.sub(r'<[^>]+>','', s or '')
    s = s.replace('&#x27;',"'").replace('&amp;','&').replace('&quot;','"').replace('&lt;','<').replace('&gt;','>').replace('&nbsp;',' ')
    return re.sub(r'\s+',' ', s).strip()

def extract(item):
    code, cat, sub, ico, dv, url = item
    path = f'{BASE}/bulk_html/{code.replace("/","_")}.html'
    if not os.path.exists(path): return None
    with open(path,'r',encoding='utf-8',errors='replace') as f:
        html = f.read()

    # ---- name + price from JSON-LD ----
    name = code
    price = ''
    msrp = ''
    for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL):
        try:
            d = json.loads(m.group(1))
            if isinstance(d,dict) and d.get('@type','').lower()=='product':
                name = d.get('name') or name
                off = d.get('offers') or {}
                if isinstance(off,dict):
                    price = str(off.get('price') or '')
                    psp = off.get('priceSpecification') or {}
                    if isinstance(psp,dict): msrp = str(psp.get('price') or '')
        except: pass

    # ---- all product-specific CDN images (strip /content/dam/channel/wcms/sa_en prefix) ----
    imgs = sorted(set(re.findall(r'/content/dam/channel/wcms/sa_en/[^"\' )]+?\.(?:jpg|jpeg|png|webp)', html)))
    imgs = [i for i in imgs if '/renditions/' not in i and '/jcr:content/' not in i]
    # code segment for filtering - only product-relevant paths
    code_lower = code.lower().replace('-','')
    code_variants = {code_lower, code.lower(), code.lower().replace('-','_')}
    # category path hints
    cat_hints = {
        'Fridge':['/refrigerator','fridge','multi-door','side-by-side','top-freezer','instaview'],
        'Washer':['/washing','washer','washtower','front-load','top-load','twin-tub','combo'],
        'Dryer':['/dryer','dryer','heat-pump'],
        'Vacuum':['/vacuum','cord','a9','a9k','slim'],
        'Dish':['/dishwasher','dfc'],
        'TV':['/tv','qned','oled','miniled'],
        'Audio':['/av/','speaker','soundbar','xboom','bounce','grab','stage'],
        'Monitor':['/mn/','monitor','smart-monitor','ultragear','gaming','myview'],
        'Cooking':['/cook','oven','cooker','lsel','electric-cooker'],
    }
    hints = cat_hints.get(cat, [])
    def is_relevant(i):
        il = i.lower()
        # Must match product code OR include category hint
        for v in code_variants:
            if v and len(v)>=5 and v in il: return True
        for h in hints:
            if h in il: return True
        return False
    # Skip global banners
    def not_global(i):
        return not any(x in i for x in ['/gnb/','/home-page/','/banners-20','/ai-core-tech','/2025-webos/webos-microsite','/common-icon/','/elements/icons-line/','/logo','/members-offer','/multishop','/ministry-of','/oled-speaker/gnb','/spring-sale','/next-day','/watch-it-promo','/av-wm-pto','/bundles-jan','/buy-one-get','/alrajhi'])
    imgs = [i for i in imgs if is_relevant(i) and not_global(i)]

    # Partition: gallery vs features
    gallery = [i for i in imgs if ('/gallery/' in i.lower() or '-gallery-' in i.lower() or '/basic' in i.lower()) and 'feature' not in i.lower()]
    # Feature images: filenames containing 'feature' AND desktop marker
    feat_all = [i for i in imgs if 'feature' in i.lower()]
    feat_d = [i for i in feat_all if re.search(r'(?:-d(?:-\d+)?(?:_\d+)?\.|/desktop/|-desktop[-.])', i.lower())]
    if not feat_d:
        # fallback - all features if no desktop markers
        feat_d = [i for i in feat_all if not re.search(r'-m[-.]|-mobile|/mobile/|-t\.', i.lower())]
    feat_d = sorted(set(feat_d))
    gallery = sorted(set(gallery))

    # Strip prefix
    PREFIX = '/content/dam/channel/wcms/sa_en'
    gallery_rel = [i[len(PREFIX):] if i.startswith(PREFIX) else i for i in gallery]
    feat_rel = [i[len(PREFIX):] if i.startswith(PREFIX) else i for i in feat_d]

    # Extract title+description near each feature image
    features_out = []
    for fn_full, fn_rel in zip(feat_d, feat_rel):
        nm = fn_full.split('/')[-1]
        idx = html.find(nm)
        if idx < 0: continue
        snip = html[max(0,idx-2500):idx+2500]
        hs = re.findall(r'<h[23456][^>]*>([\s\S]{1,250}?)</h[23456]>', snip)
        titles = []
        for h in hs:
            t = clean_html(h)
            if t and 5 < len(t) < 150 and 'Cookie' not in t and 'Share' not in t:
                titles.append(t)
        ps = re.findall(r'<p[^>]*>([\s\S]{30,800}?)</p>', snip)
        descs = []
        for p in ps:
            t = clean_html(p)
            if t and 25 < len(t) < 400 and not any(x in t.lower() for x in ['cookie','share this','cartmodel','you can share the items','absolutely necessary','functional cookies']):
                descs.append(t)
        title = titles[0] if titles else ''
        desc = ''
        if descs:
            # pick shortest meaningful desc
            descs.sort(key=len)
            for d in descs:
                if d != title and not d.startswith('*'):
                    desc = d; break
            if not desc: desc = descs[0]
        # alt key from filename
        base = nm.rsplit('.',1)[0]
        alt_match = re.search(r'feature[-_]?(\d+[-_]\d*[-_]?[a-z0-9\-]*?)(?:[-_]d|[-_]desktop|$)', base, re.I)
        alt = (alt_match.group(1) if alt_match else base[:30]).replace('-',' ').strip().title()[:25]
        if not alt: alt = f'Feature {len(features_out)+1}'
        features_out.append({'a':alt,'p':fn_rel,'t':title or alt,'d':desc or title or ''})

    # Gallery labels (best-effort)
    gallery_out = []
    for g, g_rel in zip(gallery, gallery_rel):
        nm = g.split('/')[-1].lower()
        label = 'Gallery'
        if 'basic' in nm: label = 'Basic'
        elif 'dz-' in nm or 'dz_' in nm or 'zoom-' in nm: label = 'Zoom'
        elif 'mz-' in nm or 'mz_' in nm: label = 'Mobile Zoom'
        elif re.search(r'/s-\d|gallery-s-', nm): label = 'Small'
        elif re.search(r'gallery-0?1|gallery-01', nm): label = 'Front'
        elif re.search(r'gallery-0?2|-02', nm): label = 'Angled'
        elif re.search(r'gallery-0?3|-03', nm): label = 'Side'
        elif re.search(r'gallery-0?4|-04', nm): label = 'Rear'
        elif re.search(r'gallery-0?5|-05', nm): label = 'Top'
        elif re.search(r'gallery-0?6|-06', nm): label = 'Detail'
        elif 'thumbnail' in nm: label = 'Thumbnail'
        else:
            mn = re.search(r'(?:gallery[-_])?(\d+)', nm)
            if mn: label = f'Gallery {mn.group(1)}'
        gallery_out.append({'a':label,'p':g_rel})

    # Specs
    pairs = re.findall(r'c-compare-selling__spec-name"><p>([\s\S]*?)</p></div><div class="cmp-text c-compare-selling__spec-desc"><p>([\s\S]*?)</p>', html)
    specs = {}
    for k,v in pairs:
        k = clean_html(k).rstrip(':').rstrip('\t').strip()
        v = clean_html(v)
        if k and v and k not in specs:
            # Keep short key
            k_short = k[:40]
            specs[k_short] = v[:200]
        if len(specs) >= 25: break

    return {
        'code': code, 'cat': cat, 'sub': sub, 'ico': ico, 'dv': dv, 'url': url,
        'name': name, 'price': price, 'msrp': msrp,
        'gallery': gallery_out[:25], 'features': features_out[:25], 'specs': specs,
    }

print('\nExtracting data from each PDP...')
data = []
for item in URLS:
    d = extract(item)
    if d:
        data.append(d)
        print(f'  {d["code"]}: gal={len(d["gallery"])} feat={len(d["features"])} sp={len(d["specs"])} name="{d["name"][:60]}"')
    else:
        print(f'  {item[0]}: FAILED')

# Save as JSON for next stage
with open(f'{BASE}/bulk_data.json','w',encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print(f'\nSaved bulk_data.json ({len(data)} products)')
