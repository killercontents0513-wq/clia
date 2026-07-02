"""Improved extraction: handle SKU-folder images without /gallery/ marker."""
import re, json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
PREFIX = '/content/dam/channel/wcms/sa_en'

# Same URL list as before
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

EXCLUDE_PATHS = [
    '/gnb/','/home-page/','/banners-20','/ai-core-tech','/2025-webos/webos-microsite',
    '/common-icon/','/elements/icons-line/','/members-offer','/multishop','/ministry-of',
    '/oled-speaker/gnb','/spring-sale','/next-day','/watch-it-promo','/av-wm-pto',
    '/bundles-jan','/buy-one-get','/alrajhi','/gnb-banner'
]

def clean_html(s):
    s = re.sub(r'<[^>]+>','', s or '')
    s = (s.replace('&#x27;',"'").replace('&amp;','&').replace('&quot;','"')
         .replace('&lt;','<').replace('&gt;','>').replace('&nbsp;',' ')
         .replace('\\r','').replace('\\n',' ').replace('\\t',' '))
    return re.sub(r'\s+',' ', s).strip()

def is_excluded(p):
    pl = p.lower()
    return any(x in pl for x in EXCLUDE_PATHS)

def extract(item):
    code, cat, sub, ico, dv, url = item
    path = f'{BASE}/bulk_html/{code.replace("/","_")}.html'
    if not os.path.exists(path): return None
    with open(path,'r',encoding='utf-8',errors='replace') as f: html=f.read()

    # JSON-LD
    name, price, msrp = code, '', ''
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
    # clean name
    name = (name or code).strip()

    # All CDN images
    all_imgs = sorted(set(re.findall(r'/content/dam/channel/wcms/sa_en/[^"\' )]+?\.(?:jpg|jpeg|png|webp)', html)))
    all_imgs = [i for i in all_imgs if '/renditions/' not in i and '/jcr:content/' not in i and not is_excluded(i)]

    # SKU-derived folder hints: match paths containing the code (lower, with/without dash)
    code_l = code.lower()
    code_nodash = code.lower().replace('-','')
    # detect product-specific folders by looking at count
    from collections import Counter
    folders = Counter()
    for i in all_imgs:
        parts = i.rstrip('/').split('/')
        if len(parts) >= 4:
            folder = '/'.join(parts[:-1])
            folders[folder] += 1
    # Pick folders that either (a) contain code, or (b) have MANY images (product-specific)
    product_folders = set()
    for folder, n in folders.items():
        fl = folder.lower()
        if code_l in fl or code_nodash in fl:
            product_folders.add(folder)
        elif n >= 8 and ('/images/' in fl) and any(seg in fl for seg in ['/features/','gallery','/wm/','/tvs/','/tv/','/mn/','/monitors/','/refrigerators/','/washing-machines/','/dryers/','/dishwashers/','/vacuum','/av/','/bluetooth-speakers/','/wireless-earbuds/','/home-theaters/','/ha/','/microwaves/']):
            product_folders.add(folder)

    # Also include global feature folders referenced in this PDP that contain the code or relevant feature prefix
    for i in all_imgs:
        if code_l in i.lower() or code_nodash in i.lower():
            parts = i.rstrip('/').split('/')
            if len(parts) >= 4:
                product_folders.add('/'.join(parts[:-1]))

    imgs = [i for i in all_imgs if any(pf == '/'.join(i.rstrip('/').split('/')[:-1]) for pf in product_folders)]
    # De-dup by filename (keep first)
    seen_fn = set()
    imgs = [i for i in imgs if not (i.split('/')[-1].lower() in seen_fn or seen_fn.add(i.split('/')[-1].lower()))]

    # Gallery vs Feature split
    def is_feature(p):
        pl = p.lower()
        return 'feature' in pl or '/features/' in pl
    def is_gallery(p):
        pl = p.lower()
        nm = p.split('/')[-1].lower()
        if is_feature(p): return False
        if '/gallery/' in pl or '-gallery-' in pl: return True
        # SKU folder with D-NN, DZ-NN, S-NN, MZ-NN, Z-NN, L01, 450 patterns
        if re.match(r'^(d|dz|mz|s|z|l)[-_]?\d+\.', nm): return True
        if re.match(r'^\d{3}[\._]', nm): return True  # 450.jpg
        if 'basic' in nm and ('450' in nm or 'large' in nm or nm.endswith('_basic.jpg') or 'basic_' in nm): return True
        if re.match(r'^\d+-\d+\.', nm): return True  # 1-2010.jpg
        # thumbnail/zoom indicators in SKU folder
        if re.search(r'basic|zoom|thumbnail|hr-images', nm): return True
        return False

    gallery_raw = [i for i in imgs if is_gallery(i)]
    feature_raw = [i for i in imgs if is_feature(i)]

    # Prefer desktop features: filter out mobile where desktop exists
    def is_desktop(p):
        pl = p.lower()
        return bool(re.search(r'(?:[-_]d(?:[-_]\d+)?\.|/desktop/|[-_]desktop[-.])', pl))
    def is_mobile(p):
        pl = p.lower()
        return bool(re.search(r'[-_]m(?:obile)?(?:[-_]\d+)?\.|/mobile/|[-_]mobile[-.]', pl))
    desktop_feats = [i for i in feature_raw if is_desktop(i)]
    if len(desktop_feats) >= 3:
        feat_final = desktop_feats
    else:
        # include all non-mobile features
        feat_final = [i for i in feature_raw if not is_mobile(i)] or feature_raw

    # Rank gallery: basic > large > DZ > gallery-NN > D-NN > others; drop small variants
    def gallery_rank(p):
        nm = p.split('/')[-1].lower()
        if 'basic-large' in nm or 'basic_large' in nm: return 1
        if '2010' in nm: return 2
        if re.match(r'^dz[-_]', nm) or nm.startswith('zoom') or 'zoom' in nm: return 3
        if 'gallery-0' in nm or 'gallery_' in nm: return 4
        if re.match(r'^d[-_]\d+', nm): return 5
        if '450' in nm or 'basic' in nm: return 6
        if re.match(r'^s[-_]', nm): return 8
        if re.match(r'^(mz|m)[-_]', nm): return 9
        if 'thumbnail' in nm: return 9
        return 7
    gallery_sorted = sorted(gallery_raw, key=lambda p:(gallery_rank(p), p))
    # Prefer one per "position" - group by position number
    def pos_key(p):
        nm = p.split('/')[-1].lower()
        m = re.search(r'(\d{1,2})(?=\.|[-_])', nm)
        return m.group(1) if m else nm
    seen_pos = {}
    gallery_final = []
    for p in gallery_sorted:
        k = pos_key(p)
        # Prefer larger/basic versions - keep the first (better-ranked) one per position
        if k not in seen_pos:
            seen_pos[k] = True
            gallery_final.append(p)
    # Limit
    gallery_final = gallery_final[:25]
    feat_final = feat_final[:25]

    # Strip prefix
    def rel(p): return p[len(PREFIX):] if p.startswith(PREFIX) else p

    # Extract feature title/desc near each image
    features_out = []
    for fn_full in feat_final:
        nm = fn_full.split('/')[-1]
        idx = html.find(nm)
        if idx < 0: continue
        snip = html[max(0,idx-2500):idx+2500]
        hs = re.findall(r'<h[23456][^>]*>([\s\S]{1,250}?)</h[23456]>', snip)
        titles = []
        for h in hs:
            t = clean_html(h)
            if t and 5 < len(t) < 150 and 'Cookie' not in t and 'Share' not in t and 'cartModel' not in t.lower():
                titles.append(t)
        ps = re.findall(r'<p[^>]*>([\s\S]{30,900}?)</p>', snip)
        descs = []
        for p in ps:
            t = clean_html(p)
            if 25 < len(t) < 400 and not any(x in t.lower() for x in ['cookie','share this','cartmodel','you can share','absolutely necessary','functional cookies','what people are','our picks','need help','our story']):
                descs.append(t)
        title = titles[0] if titles else ''
        desc = ''
        # prefer shortest non-duplicate, non-bullet
        descs2 = [d for d in descs if d != title and not d.startswith('*')]
        if descs2:
            descs2.sort(key=len)
            desc = descs2[0]
        elif descs:
            desc = descs[0]
        # Derive alt/label from filename
        base = nm.rsplit('.',1)[0]
        alt_match = re.search(r'feature[-_]?(\d+[-_]?\d*[-_]?[a-z0-9\-]*?)(?:[-_]d|[-_]desktop|$)', base, re.I)
        alt = (alt_match.group(1) if alt_match else base[:30]).replace('-',' ').replace('_',' ').strip().title()[:25] or 'Feature'
        features_out.append({'a':alt,'p':rel(fn_full),'t':title or alt, 'd':desc or title or ''})

    # Gallery labels
    gallery_out = []
    for g in gallery_final:
        nm = g.split('/')[-1].lower()
        if 'basic-large' in nm: label='Basic Large'
        elif 'basic' in nm: label='Basic'
        elif re.match(r'^dz[-_]?(\d+)', nm):
            num = re.match(r'^dz[-_]?(\d+)', nm).group(1)
            label=f'Zoom {int(num)}'
        elif re.match(r'^(d|s|mz|z|l)[-_]?(\d+)', nm):
            num = re.match(r'^(?:[a-z])[-_]?(\d+)', nm).group(1)
            label=f'View {int(num)}'
        elif 'gallery-' in nm:
            m = re.search(r'gallery[-_]?(\d+)', nm)
            label = f'Gallery {int(m.group(1))}' if m else 'Gallery'
        elif '2010' in nm:
            m = re.search(r'(\d+)[-_]?2010', nm)
            label = f'Gallery {int(m.group(1))}' if m else 'Gallery'
        elif re.match(r'^\d{3}[\._]', nm): label='Thumbnail'
        else:
            m = re.search(r'(\d+)', nm)
            label = f'View {int(m.group(1))}' if m else 'Detail'
        gallery_out.append({'a':label,'p':rel(g)})

    # Specs
    pairs = re.findall(r'c-compare-selling__spec-name"><p>([\s\S]*?)</p></div><div class="cmp-text c-compare-selling__spec-desc"><p>([\s\S]*?)</p>', html)
    specs = {}
    for k,v in pairs:
        k = clean_html(k).rstrip(':').rstrip('\t').strip()
        v = clean_html(v)
        if k and v and k not in specs:
            specs[k[:40]] = v[:200]
        if len(specs) >= 30: break

    return {
        'code': code, 'cat': cat, 'sub': sub, 'ico': ico, 'dv': dv, 'url': url,
        'name': name, 'price': price, 'msrp': msrp,
        'gallery': gallery_out, 'features': features_out, 'specs': specs,
    }

print('Extracting (v2)...')
data = []
for item in URLS:
    d = extract(item)
    if d:
        data.append(d)
        print(f'  {d["code"]:12s}: gal={len(d["gallery"]):2d} feat={len(d["features"]):2d} sp={len(d["specs"]):2d} pr={d["price"]:>6s} name="{d["name"][:55]}"')

with open(f'{BASE}/bulk_data.json','w',encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print(f'\nSaved bulk_data.json ({len(data)})')
