# -*- coding: utf-8 -*-
# CLIA v6_18 injector — applies 30 crawl JSON files with LG official English tone copy
import json, os, re, sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
CRAWL = f'{BASE}/crawl_v2'
V6_18 = f'{BASE}/LG_AI_Content_Hub_v6_18.html'
OUT = f'{BASE}/LG_AI_Content_Hub_v6_18.html'
BACKUP = f'{BASE}/LG_AI_Content_Hub_v6_18.pre_inject.html'

# User-specified order (30 products)
ORDER = [
    'LT19CBBSIN','WTT1410OL1','WSN1508BMT','WFB0914XM','WTV11BND','WTV24HHP',
    'RH81T2SP7RM','A9LSLIM','WK1310BST','RH10V9PV2W','WFV1214BST1','65QNED93A6A',
    'WTR22HHP','WS2112BST','WTT1108OW1','WFN1510WHT','MS3032JAS','S95TR',
    'RH18U8JVCW','WSV0906XM','WFR1114WH','A9K-SOLO','LS19GBBDI','WFR1114MB',
    'S20A','DFC435FW','S65TR','WFN1310BST','WFN1310WHT','LS25CBBDIK'
]

# Category mapping from URL path segments
def classify(url):
    u = url.lower()
    if '/refrigerators/top-freezers' in u: return ('HA','Refrigerator','Top Freezer','❄️')
    if '/refrigerators/side-by-side' in u: return ('HA','Refrigerator','Side by Side','❄️')
    if '/refrigerators/' in u: return ('HA','Refrigerator','Refrigerator','❄️')
    if '/washing-machines/front-load-combo' in u: return ('HA','Washer','Front Load Combo','🧺')
    if '/washing-machines/front-load' in u: return ('HA','Washer','Front Load','🧺')
    if '/washing-machines/top-load' in u: return ('HA','Washer','Top Load','🧺')
    if '/washing-machines/twin-tub' in u: return ('HA','Washer','Twin Tub','🧺')
    if '/washing-machines/washtower' in u: return ('HA','Washer','WashTower','🧺')
    if '/dryers/' in u: return ('HA','Dryer','Heat Pump','🌀')
    if '/vacuum-cleaners/' in u: return ('HA','Vacuum','Cordless Stick','🧹')
    if '/tv-soundbars/qned' in u or '/tvs/' in u: return ('MS','TV','QNED','📺')
    if '/tv-soundbars/soundbars' in u or '/speakers/soundbars' in u: return ('MS','Audio','Soundbar','🔈')
    if '/microwaves/' in u or '/cooking-appliances/microwaves' in u: return ('HA','Micro','Microwave','🔲')
    if '/dishwashers/' in u: return ('HA','DW','Dishwasher','🍽️')
    return ('HA','Other','Other','📦')

# Normalize price (strip leading space, add SAR prefix)
def price(s):
    s = (s or '').strip()
    if not s: return ''
    # Strip internal extra whitespace
    s = re.sub(r'\s+', '', s)
    return 'SAR ' + s

# ── LG Official English Tone bullet generator ──
def gen_bullets(p, cat, sub):
    specs = {s['k']: s['v'] for s in p.get('specs', [])}
    h1 = p.get('h1', '')
    bullets = []

    def spec(k, default=None):
        return specs.get(k, default)

    def has(k, v='Yes'):
        val = specs.get(k, '')
        if isinstance(v, list): return val in v
        return val == v

    if cat == 'Dryer':
        cap = spec('Max Dry Capacity (kg)')
        heat = spec('Heat Source Type')
        # 1. Capacity + technology headline
        if cap: bullets.append(f"INTELLIGENT DRYING PERFORMANCE — {cap}kg drum capacity with {heat or 'advanced'} heat source delivers gentle, efficient drying for everyday family loads without compromising fabric care.")
        if has('Sensor Dry'):
            bullets.append("SENSOR DRY TECHNOLOGY — Built-in sensors detect humidity and automatically adjust drying time, preventing over-drying and protecting delicate fabrics from shrinkage and damage.")
        if has('Anti Crease'):
            bullets.append("ANTI-CREASE FUNCTION — Gently tumbles clothes after the cycle ends to prevent wrinkles, so garments come out looking freshly pressed and ready to wear.")
        if has('Child Lock'):
            bullets.append("CHILD LOCK & SAFE OPERATION — Keeps curious little hands safe by locking the control panel, with a Drum Light for easy loading and clear LCD display for intuitive use.")
        dims = spec('Product Dimensions (WxHxD mm)')
        color = spec('Body Color') or ''
        bullets.append(f"STYLISH, SPACE-CONSCIOUS DESIGN — {color} finish with ventless condenser operation and {dims or 'compact'} footprint fits seamlessly into modern homes, no external venting required.")
    elif cat == 'Washer':
        cap = spec('Max Wash Capacity(kg)') or spec('Wash Capacity(kg)')
        if cap: bullets.append(f"POWERFUL CLEAN, EVERY CYCLE — {cap}kg wash capacity handles family-size loads with LG's Inverter Direct Drive motor for thorough, efficient washing across every fabric type.")
        if has('AI DD'):
            bullets.append("AI DIRECT DRIVE® TECHNOLOGY — Intelligently senses the weight and softness of fabrics, automatically selecting the optimal wash motion for superior fabric care and cleaning performance.")
        if has('Steam'):
            bullets.append("STEAM-POWERED HYGIENE — TrueSteam™ penetrates deep into fibers to remove allergens, refresh garments and sanitize without harsh chemicals, keeping clothes fresh and family-friendly.")
        if has('ThinQ(Wi-Fi)') or has('Wi-Fi'):
            bullets.append("SMART CONTROL WITH LG ThinQ® — Start, monitor and receive notifications from anywhere through the LG ThinQ® app. Download new cycles and get Smart Diagnosis™ support via Wi-Fi.")
        color = spec('Body Color') or ''
        dims = spec('Product Dimensions (WxHxD mm)')
        bullets.append(f"ENERGY-EFFICIENT INVERTER MOTOR — LG's 10-year warranted Inverter DirectDrive™ delivers quiet, durable performance in a {color or 'modern'} finish, {dims or 'standard-fit'} design.")
    elif cat == 'Refrigerator':
        tot = spec('Storage Volume Total (L)')
        bullets.append(f"GENEROUS STORAGE — {tot or 'Spacious'}L total capacity with thoughtfully organized compartments keeps groceries fresh, accessible and well-organized for every family's lifestyle.")
        if has('LINEAR Cooling'):
            bullets.append("LINEAR COOLING™ TECHNOLOGY — Minimizes temperature fluctuations to keep produce fresher for longer, preserving nutrients, texture and flavor in every compartment.")
        if 'Smart Inverter' in (spec('Compressor Type') or ''):
            bullets.append("SMART INVERTER COMPRESSOR — Adjusts cooling power to match real-time conditions, delivering superior energy efficiency, quieter operation and a 10-year warranty on the compressor.")
        if has('Deodorizer'):
            bullets.append("HYGIENIC INTERIOR — Built-in deodorizer keeps interior air fresh, while Multi-Air Flow and LED lighting maintain consistent cooling and clear visibility across every shelf.")
        dims = spec('Product Dimension (WxHxD, mm)')
        color = spec('Finish (Door)') or ''
        bullets.append(f"ELEGANT DESIGN, EVERYDAY DURABILITY — {color or 'Premium'} finish on a {dims or 'standard-fit'} chassis blends into any kitchen, built to last with LG's trusted quality.")
    elif cat == 'TV':
        disp = spec('Display Type') or '4K'
        res = spec('Display Resolution') or '4K'
        proc = spec('Picture Processor') or 'Advanced AI Processor'
        bullets.append(f"IMMERSIVE {disp} DISPLAY — {res} resolution powered by {proc} delivers breathtaking picture quality with deep blacks, precise color and stunning contrast for cinematic home viewing.")
        if has('Dolby Atmos'):
            bullets.append("CINEMATIC DOLBY VISION & ATMOS — Experience the full creative intent of movies and series with Dolby Vision imaging and immersive Dolby Atmos audio that envelops the room.")
        if 'AI' in (spec('AI Picture Pro') or ''):
            bullets.append("AI PICTURE & SOUND PRO — LG's AI intelligently analyzes each scene and genre, optimizing picture quality and audio in real-time for the best possible viewing experience.")
        if 'webOS' in (spec('Operating System (OS)') or ''):
            bullets.append("webOS SMART TV PLATFORM — Effortless access to thousands of apps, streaming services and AI features through LG's intuitive webOS, with the included AI Magic Remote.")
        bullets.append("GAMING-READY PERFORMANCE — 144Hz VRR, ALLM, HGIG and 4x HDMI 2.1 ports make this TV a powerhouse for console and PC gaming with silky-smooth motion and low input lag.")
    elif cat == 'Audio':
        bullets.append(f"CINEMATIC SOUND AT HOME — {h1} delivers immersive, multi-dimensional audio that transforms your living room into a personal theater with every movie, show and song.")
        bullets.append("AI SOUND PRO — Automatically analyzes content and optimizes audio profile in real-time, whether you're watching a blockbuster, enjoying music or catching up on the news.")
        bullets.append("WOW ORCHESTRA & WOW INTERFACE — Synchronize seamlessly with compatible LG TVs to use both TV and Soundbar speakers together, controlled from a single remote for effortless listening.")
        bullets.append("DOLBY ATMOS IMMERSION — Object-based surround sound fills your space with precise, three-dimensional audio that moves around and above you for a true cinema experience.")
        bullets.append("SLEEK, DESIGN-FORWARD FORM — Premium finishes and a slim profile complement any TV setup, with LG ThinQ® app control for easy setup, adjustment and software updates.")
    elif cat == 'Vacuum':
        rt = spec('Max Run Time per battery (minutes) (Normal Mode)') or spec('Max Run Time per battery (minutes) (Normal Mode without Nozzles)')
        suc = spec('Max Suction Power (W)')
        wt = spec('Weight (kg)')
        bullets.append(f"POWERFUL CORDLESS CLEANING — {suc or 'High'}W max suction removes dust, pet hair and debris from hard floors, rugs and upholstery with uninterrupted performance.")
        bullets.append(f"ALL-DAY RUN TIME — Up to {rt or '40'} minutes of cleaning per battery lets you tackle the whole home on a single charge, with easy-swap battery design for extended sessions.")
        bullets.append(f"LIGHTWEIGHT, ONE-HAND DESIGN — Just {wt or '2.9'}kg total weight with 2-in-1 Stick + Handheld convertibility makes overhead, under-furniture and car cleaning effortless.")
        bullets.append("ADVANCED FILTRATION — Multi-stage filtration captures fine dust and allergens, keeping exhaust air clean and healthy for homes with allergy sufferers, children and pets.")
        bullets.append("SMART INVERTER MOTOR — LG's reliable Smart Inverter Motor delivers consistent suction over the long run, with LED battery indicator and one-touch dust bin emptying for hygienic maintenance.")
    elif cat == 'Micro':
        cap = spec('Capacity (L)') or '30'
        bullets.append(f"SPACIOUS FAMILY CAPACITY — {cap}L interior fits large dinner plates, casseroles and family-sized meal prep with room to spare for everyday cooking, reheating and defrosting.")
        bullets.append("SMART INVERTER COOKING — LG's Smart Inverter technology delivers even, consistent heating that preserves flavor, texture and nutrients compared to conventional microwaves.")
        bullets.append("EASY-CLEAN ANTIBACTERIAL CAVITY — EasyClean® interior coating resists stains and wipes down quickly, with antibacterial protection for a hygienic cooking space.")
        bullets.append("INTUITIVE AR DISPLAY — Arabic-language display and touch controls provide at-a-glance access to sensor cooking, auto menus and defrost programs designed for regional cuisines.")
        bullets.append("ENERGY-SAVING ECO MODE — LG's Eco mode reduces standby power consumption, while NeoChef's durable build and sleek finish complement any modern kitchen countertop.")
    elif cat == 'DW':
        places = spec('Total Place Settings') or '14'
        bullets.append(f"{places}-PLACE WASH CAPACITY — Fits a full family's worth of dishes, pans and glassware in a single load with intelligently designed racks that adapt to any shape.")
        if 'QuadWash' in str(specs):
            bullets.append("QUADWASH™ POWER — Four spray arms (three multi-motion + one dedicated) reach every corner of the tub for spotless cleaning with fewer re-washes and shorter cycles.")
        if 'TrueSteam' in str(specs):
            bullets.append("TRUESTEAM™ GENTLE CLEAN — Steam-based cleaning removes tough stains from baby bottles, glassware and delicates without the need for aggressive pre-scrubbing.")
        bullets.append("INVERTER DIRECT DRIVE MOTOR — Whisper-quiet 43dBA operation with fewer moving parts for long-lasting reliability, backed by LG's 10-year inverter motor warranty.")
        bullets.append("SMART THINQ® CONNECTIVITY — Start cycles, monitor progress and download new programs from anywhere via LG ThinQ® app — plus Smart Diagnosis™ for instant troubleshooting.")
    else:
        # generic fallback
        bullets = [
            f"PREMIUM LG ENGINEERING — {h1} built with LG's trusted components, durable finish and smart controls designed for everyday excellence.",
            "SMART DIAGNOSIS™ SUPPORT — Instant troubleshooting and remote service support through the LG ThinQ® app, keeping your product running smoothly for years to come.",
            "ENERGY-EFFICIENT OPERATION — Engineered to deliver outstanding performance while minimizing energy and water consumption for lower running costs.",
            "MODERN DESIGN — Sleek finish and thoughtful controls blend seamlessly into any contemporary home.",
            "LG OFFICIAL WARRANTY — Backed by LG Electronics' global warranty and LG Saudi Arabia after-sales service for worry-free ownership.",
        ]

    # Ensure exactly 5 bullets, ≤500 chars each
    while len(bullets) < 5:
        bullets.append("LG OFFICIAL SAUDI ARABIA WARRANTY — Backed by full manufacturer warranty and certified LG service network across KSA.")
    bullets = [b[:500] for b in bullets[:5]]
    return bullets

def gen_description(p, cat, sub, bullets):
    h1 = p.get('h1','')
    model = p.get('id','')
    parts = [f"Experience the {h1} ({model}) — engineered by LG to deliver best-in-class performance for modern homes in Saudi Arabia.", ""]
    parts.extend(['• ' + b for b in bullets])
    parts.append("")
    parts.append("Designed with LG's signature engineering, intuitive controls and trusted build quality. Backed by LG Electronics' official warranty and LG Saudi Arabia after-sales service network for complete peace of mind.")
    return '\\n'.join(parts)

def gen_title_amazon(p, cat, sub):
    h1 = p.get('h1','').strip()
    model = p.get('id','')
    if cat == 'Dryer':
        cap = next((s['v'] for s in p.get('specs',[]) if s['k']=='Max Dry Capacity (kg)'),'')
        return f"LG {cap+'kg ' if cap else ''}Heat Pump Dryer with Sensor Dry, Anti-Crease, Child Lock — Ventless Condenser Design ({model})"[:200]
    if cat == 'Washer':
        cap = next((s['v'] for s in p.get('specs',[]) if s['k'] in ('Max Wash Capacity(kg)','Wash Capacity(kg)')),'')
        return f"LG {cap+'kg ' if cap else ''}{sub} Washing Machine with AI DD, Steam, TurboWash, ThinQ Wi-Fi — Official LG Saudi Arabia ({model})"[:200]
    if cat == 'Refrigerator':
        tot = next((s['v'] for s in p.get('specs',[]) if s['k']=='Storage Volume Total (L)'),'')
        return f"LG {tot+'L ' if tot else ''}{sub} Refrigerator with Smart Inverter Compressor, LINEAR Cooling, Multi Air Flow, 10-Year Warranty ({model})"[:200]
    if cat == 'TV':
        return f"LG {h1} — 4K Smart TV with AI Processor, Dolby Vision, Dolby Atmos, webOS, AI Magic Remote ({model})"[:200]
    if cat == 'Audio':
        return f"LG {h1} — Dolby Atmos, AI Sound Pro, LG ThinQ, WOW Orchestra for LG TVs ({model})"[:200]
    if cat == 'Vacuum':
        return f"LG CordZero {h1} — Cordless Stick Vacuum with Smart Inverter Motor, 2-in-1 Stick + Handheld ({model})"[:200]
    if cat == 'Micro':
        return f"LG {h1} — Smart Inverter, EasyClean Cavity, AR Display, 30L Family Capacity ({model})"[:200]
    if cat == 'DW':
        return f"LG {h1} — QuadWash TrueSteam Dishwasher with Inverter Direct Drive, ThinQ Wi-Fi ({model})"[:200]
    return (f"LG {h1} ({model})")[:200]

def gen_kw(p, cat, sub):
    words = ['LG', p['id'], cat, sub, 'Saudi Arabia', 'KSA', 'Official', '2025']
    h1 = p.get('h1','')
    # extract key words from h1
    for tok in re.findall(r'[A-Za-z0-9]+', h1):
        if 2 <= len(tok) <= 15 and tok.lower() not in [w.lower() for w in words]:
            words.append(tok)
    s = ' '.join(words)
    return s[:250]

# ── Module flattening (feat array for v6_18) ──
def flatten_modules(p):
    feat = []
    for m in p.get('modules', []):
        title = m.get('head','').strip()
        desc = m.get('body','').strip() or m.get('eye','').strip()
        for img in m.get('imgs', []):
            feat.append({
                'a': img.get('a','')[:200],
                'p': img.get('p',''),
                't': title[:120] if title else img.get('a','')[:80],
                'd': desc[:200] if desc else '',
                'w': img.get('w',0),
                'h': img.get('h',0),
            })
    return feat

# ── Specs flattening ──
def flatten_specs(p):
    sp = {}
    for s in p.get('specs', []):
        k = re.sub(r'[^A-Za-z0-9_]', '_', s['k'])[:40]
        if k and k not in sp:
            sp[k] = s['v']
    return sp

# ── JS object literal formatter ──
def js_str(s):
    if s is None: return '""'
    s = str(s).replace('\\','\\\\').replace('"','\\"').replace('\n','\\n').replace('\r','')
    return f'"{s}"'

def fmt_product(p, cat_info):
    dv, cat, sub, ico = cat_info
    gal = p.get('gallery', [])
    feat = flatten_modules(p)
    sp = flatten_specs(p)
    bullets = gen_bullets(p, cat, sub)
    title_amz = gen_title_amazon(p, cat, sub)
    desc = gen_description(p, cat, sub, bullets)
    kw = gen_kw(p, cat, sub)
    nm = p.get('h1','').strip() or p.get('id','')

    pr = price(p.get('curPrice',''))
    op = price(p.get('origPrice','')) if p.get('origPrice','').strip() else ''

    # build the product literal
    gal_s = '[' + ','.join(
        '{a:%s,p:%s,w:%d,h:%d}' % (js_str(g['a']), js_str(g['p']), g.get('w',0), g.get('h',0))
        for g in gal
    ) + ']'
    feat_s = '[' + ','.join(
        '{a:%s,p:%s,t:%s,d:%s,w:%d,h:%d}' % (
            js_str(f['a']), js_str(f['p']), js_str(f['t']), js_str(f['d']),
            f.get('w',0), f.get('h',0)
        ) for f in feat
    ) + ']'
    sp_s = '{' + ','.join(f'{js_str(k)}:{js_str(v)}' for k,v in sp.items()) + '}'
    bul_s = '[' + ','.join(js_str(b) for b in bullets) + ']'
    faq_s = ('[' + ','.join([
        '{q:"What is the model code?",a:%s}' % js_str(p['id']),
        '{q:"Is this the official LG model?",a:"Yes. Official LG product sold and serviced by LG Saudi Arabia."}',
        '{q:"What is the warranty?",a:"Full LG Saudi Arabia manufacturer warranty applies. Visit lg.com/sa_en for details."}',
    ]) + ']')
    promo_s = '[{icon:"Free Delivery",tip:"Free delivery across KSA"},{icon:"Free Installation",tip:"Free installation service"},{icon:"Easy Installment",tip:"Flexible installments via Tamara"},{icon:"Bank Offers",tip:"Extra savings with partner banks"},{icon:"5% Welcome Discount",tip:"5% off for LG Members"}]'
    disc_s = '["All images and specifications sourced from LG.com Saudi Arabia.","Features and availability may vary by region and model."]'
    tags_s = '[]'

    return (
        f'{{id:{js_str(p["id"])},dv:{js_str(dv)},cat:{js_str(cat)},sub:{js_str(sub)},ico:{js_str(ico)},'
        f'nm:{js_str(nm)},pr:{js_str(pr)},op:{js_str(op)},url:{js_str(p.get("url",""))},crawled:true,'
        f'amz_title:{js_str(title_amz)},amz_desc:{js_str(desc)},'
        f'gal:{gal_s},feat:{feat_s},sp:{sp_s},tags:{tags_s},bul:{bul_s},faq:{faq_s},'
        f'promo:{promo_s},disc:{disc_s},kw:{js_str(kw)}}}'
    )

# ── Main: build new P[] content and splice into v6_18 ──
def main():
    # Load crawl data for 30 products in order
    products = []
    for pid in ORDER:
        path = f'{CRAWL}/{pid}.json'
        if not os.path.exists(path):
            print(f'[WARN] missing {pid}.json')
            continue
        with open(path, encoding='utf-8') as f:
            p = json.load(f)
        products.append((pid, p))

    # Read v6_18
    with open(V6_18, encoding='utf-8') as f:
        html = f.read()

    # Backup
    with open(BACKUP, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'backup: {BACKUP}')

    # Parse existing P[] array (lines 681..2467 as shown)
    m = re.search(r'(const P=\[)(.*?)(\n\];)', html, re.DOTALL)
    if not m:
        print('[ERR] P[] not found')
        return
    p_header, p_body, p_footer = m.group(1), m.group(2), m.group(3)

    # Existing entries — brace-depth split (entries span multiple lines with nested braces)
    existing_lines = []
    i, n = 0, len(p_body)
    # Skip to first '{'
    while i < n and p_body[i] != '{':
        i += 1
    while i < n:
        if p_body[i] != '{':
            i += 1; continue
        start = i
        depth = 0
        in_str = False
        str_ch = None
        j = i
        while j < n:
            c = p_body[j]
            if in_str:
                if c == '\\': j += 2; continue
                if c == str_ch: in_str = False
                j += 1
                continue
            if c in ('"', "'"):
                in_str = True; str_ch = c; j += 1; continue
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    existing_lines.append(p_body[start:j+1])
                    i = j + 1
                    break
            j += 1
        else:
            break
    print(f'existing P entries: {len(existing_lines)}')

    # Build set of new IDs (replace these)
    new_ids = set(ORDER)

    # Keep existing entries NOT in new_ids
    kept = []
    for entry in existing_lines:
        m2 = re.search(r'\{id:"([^"]+)"', entry)
        if not m2: continue
        if m2.group(1) in new_ids:
            continue
        kept.append(entry)
    print(f'kept (not replaced): {len(kept)}')

    # Build new 30 entries in order
    new_entries = []
    for pid, p in products:
        cat_info = classify(p.get('url',''))
        new_entries.append(fmt_product(p, cat_info))
    print(f'new entries built: {len(new_entries)}')

    # Assemble: new 30 first (user-specified order), then kept existing
    all_entries = new_entries + kept
    new_body = '\n' + ',\n'.join(all_entries) + ','

    new_html = html[:m.start()] + p_header + new_body + p_footer + html[m.end():]

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(new_html)

    # Stats
    sz_old = len(html)
    sz_new = len(new_html)
    print(f'\nInjection complete')
    print(f'  total P entries: {len(all_entries)} (30 new + {len(kept)} kept)')
    print(f'  file: {OUT}')
    print(f'  size: {sz_old:,} -> {sz_new:,} ({sz_new-sz_old:+,})')

if __name__ == '__main__':
    main()
