"""Integrate bulk_data.json entries into LG_AI_Content_Hub_v6_18.html."""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
HTML_PATH = f'{BASE}/LG_AI_Content_Hub_v6_18.html'

with open(f'{BASE}/bulk_data.json','r',encoding='utf-8') as f:
    DATA = json.load(f)

def jsstr(s):
    """Escape for double-quoted JS string used in the entry template."""
    if s is None: s = ''
    s = str(s)
    # Normalize smart quotes
    s = (s.replace('\u201c','"').replace('\u201d','"')
         .replace('\u2018',"'").replace('\u2019',"'"))
    # Escape for JS double-quoted string: backslash first, then double-quote
    s = s.replace('\\','\\\\').replace('"','\\"')
    s = s.replace('\n',' ').replace('\r','').replace('\t',' ')
    s = re.sub(r'\s+',' ', s).strip()
    return s

def format_price(v):
    if not v: return ''
    try:
        f = float(v)
        if f == int(f): return f'SAR {int(f):,}'
        return f'SAR {f:,.2f}'
    except:
        return f'SAR {v}'

# ---- default promo/disc by category ----
PROMO_DEFAULT = {
    'HA': "[{icon:\"Free Delivery\",tip:\"Free delivery across KSA\"},{icon:\"Free Installation\",tip:\"Free installation service\"},{icon:\"Easy Installment\",tip:\"Flexible installments via Tamara\"},{icon:\"Bank Offers\",tip:\"Extra savings with partner banks\"},{icon:\"5% Welcome Discount\",tip:\"5% off for LG Members\"}]",
    'MS': "[{icon:\"Free Delivery\",tip:\"Free delivery across KSA\"},{icon:\"Easy Installment\",tip:\"Flexible installments via Tamara\"},{icon:\"Bank Offers\",tip:\"Extra savings with partner banks\"},{icon:\"5% Welcome Discount\",tip:\"5% off for LG Members\"}]",
}

def build_entry(d):
    code = d['code']
    name = jsstr(d.get('name') or code)
    price = format_price(d.get('price'))
    msrp = format_price(d.get('msrp'))
    url = d['url']
    cat = d['cat']; sub = d['sub']; ico = d['ico']; dv = d['dv']

    # Gallery array
    gal_items = []
    for g in (d.get('gallery') or [])[:20]:
        w = f',w:{g["w"]},h:{g["h"]}' if g.get('w') and g.get('h') else ''
        gal_items.append(f"{{a:\"{jsstr(g['a'])}\",p:\"{jsstr(g['p'])}\"{w}}}")
    gal = '[\n' + ',\n'.join(gal_items) + '\n]' if gal_items else '[]'

    # Features array (supports composite imgs[] for multi-image modules)
    feat_items = []
    for ft in (d.get('features') or [])[:20]:
        a = jsstr(ft['a'])
        p = jsstr(ft['p'])
        t = jsstr(ft['t'])
        dd = jsstr(ft.get('d',''))
        wh = f',w:{ft["w"]},h:{ft["h"]}' if ft.get('w') and ft.get('h') else ''
        # Composite sub-images
        if ft.get('imgs') and len(ft['imgs']) >= 2:
            sub_items = []
            for im in ft['imgs']:
                ia = jsstr(im.get('a',''))
                ip = jsstr(im['p'])
                iwh = f',w:{im["w"]},h:{im["h"]}' if im.get('w') and im.get('h') else ''
                sub_items.append(f'{{a:"{ia}",p:"{ip}"{iwh}}}')
            imgs_js = ','.join(sub_items)
            feat_items.append(f"{{a:\"{a}\",p:\"{p}\",t:\"{t}\",d:\"{dd}\"{wh},imgs:[{imgs_js}]}}")
        else:
            feat_items.append(f"{{a:\"{a}\",p:\"{p}\",t:\"{t}\",d:\"{dd}\"{wh}}}")
    feat = '[\n' + ',\n'.join(feat_items) + '\n]' if feat_items else '[]'

    # Specs object - sanitize keys
    sp_items = []
    for k,v in (d.get('specs') or {}).items():
        # Use simple key: strip special chars
        key = re.sub(r'[^A-Za-z0-9]','_', k).strip('_')[:30]
        if not key or key[0].isdigit(): key = 'K_' + key
        sp_items.append(f'"{key}":"{jsstr(v)}"')
    sp = '{' + ','.join(sp_items) + '}' if sp_items else '{}'

    # Tags (derive from name/specs) — generic
    tag_src = (name + ' ' + ' '.join((d.get('specs') or {}).values())).lower()
    tag_candidates = []
    tag_patterns = ['4k','oled','miniled','qned','webos','dolby atmos','dolby vision','ai dd','ai','thinq','inverter','smart inverter','steam','turbowash','ip67','ipx4','auracast','bluetooth','usb-c','hdr10','dci-p3','144hz','480hz','60hz','240v','wi-fi']
    for tp in tag_patterns:
        if tp in tag_src and tp.title() not in tag_candidates:
            tag_candidates.append(tp.title())
    if not tag_candidates: tag_candidates = [cat, sub]
    tags = '[' + ','.join(f'"{jsstr(t)}"' for t in tag_candidates[:8]) + ']'

    # Bullets - top 5 features' titles
    bul_items = []
    for ft in (d.get('features') or [])[:8]:
        tt = jsstr(ft.get('t','')).upper()
        dd = jsstr(ft.get('d',''))
        if tt and dd and dd != ft.get('t',''):
            bul_items.append(f'"{tt}: {dd[:120]}"')
        elif tt:
            bul_items.append(f'"{tt}"')
    if not bul_items:
        # fallback to specs
        for k,v in list((d.get('specs') or {}).items())[:5]:
            bul_items.append(f'"{jsstr(k).upper()}: {jsstr(v)[:120]}"')
    bul = '[' + ','.join(bul_items) + ']' if bul_items else '[]'

    # FAQ — minimal generic
    faq = f'[{{q:"What is the model code?",a:"{code}"}}]' if not d.get('features') else ''
    if d.get('features'):
        # Pick first 2 feature titles as Q&A
        faq_items = [f'{{q:"What is the model code?",a:"{code}"}}']
        for ft in d['features'][:2]:
            tq = jsstr(ft.get('t',''))
            ta = jsstr(ft.get('d',''))
            if tq and ta:
                faq_items.append(f'{{q:"About {tq}?",a:"{ta}"}}')
        faq = '[' + ','.join(faq_items) + ']'

    promo = PROMO_DEFAULT.get(dv, PROMO_DEFAULT['MS'])
    disc = '["All images and specs from LG.com Saudi Arabia.","Features and availability may vary by region."]'

    # Keywords
    kw = jsstr(f'LG {code} {name} {cat} {sub} Saudi Arabia KSA {" ".join(tag_candidates[:5])}')

    entry = (
        f'{{id:"{code}",dv:"{dv}",cat:"{cat}",sub:"{sub}",ico:"{ico}",'
        f'nm:"{name}",pr:"{price}",op:"{msrp}",url:"{url}",crawled:true,\n'
        f'gal:{gal},\n'
        f'feat:{feat},\n'
        f'sp:{sp},tags:{tags},\n'
        f'bul:{bul},\n'
        f'faq:{faq},\n'
        f'promo:{promo},\n'
        f'disc:{disc},\n'
        f'kw:"{kw}"}}'
    )
    return entry

# Generate all entries
entries_by_code = {}
for d in DATA:
    entries_by_code[d['code']] = build_entry(d)

# Read file
with open(HTML_PATH,'r',encoding='utf-8') as f:
    html = f.read()

# Category placement map for NEW products
CAT_SECTION = {
    'TV': '// ─── TV (MS) ───',
    'Audio': '// ─── Audio (MS) ───',  # Soundbars might go here if speaker/soundbar
    'Monitor': '// ─── Monitors (MS) ───',
    'Fridge': '// ─── Refrigerator (HA) ───',
    'Washer': '// ─── Washer (HA) ───',
    'Dryer': '// ─── Dryer (HA) ───',
    'Vacuum': '// ─── Vacuum (HA) ───',
    'Dish': '// ─── Dishwasher / Microwave / Oven (HA) ───',
    'Cooking': '// ─── Dishwasher / Microwave / Oven (HA) ───',
}

# Soundbars have their own section:
SOUNDBAR_SECTION = '// ─── Soundbars (MS) ───'

new_html = html
updated = []
added = []
skipped = []

for code, entry in entries_by_code.items():
    # Try to find existing entry block: {id:"CODE", ... up to matching closing brace }
    # Simple approach: match `{id:"CODE",` then find the closing brace at same depth
    pat = re.compile(r'\{id:"' + re.escape(code) + r'",[^\n]*(?:\n(?!\{id:)[^\n]*)*', re.DOTALL)
    m = pat.search(new_html)
    if m:
        # Determine the full block span by balancing braces
        start = m.start()
        depth = 0
        end = start
        i = start
        while i < len(new_html):
            c = new_html[i]
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
            elif c == '"':
                # skip string
                i += 1
                while i < len(new_html) and new_html[i] != '"':
                    if new_html[i] == '\\': i += 1
                    i += 1
            elif c == "'":
                i += 1
                while i < len(new_html) and new_html[i] != "'":
                    if new_html[i] == '\\': i += 1
                    i += 1
            i += 1
        # Check trailing comma
        after = new_html[end:end+2]
        block = new_html[start:end]
        new_html = new_html[:start] + entry + new_html[end:]
        updated.append(code)
    else:
        # Need to insert new. Find the appropriate section.
        d = next((x for x in DATA if x['code']==code), None)
        if not d:
            skipped.append(code); continue
        cat = d['cat']; sub = d['sub']
        section_marker = CAT_SECTION.get(cat)
        if cat == 'Audio' and 'Soundbar' in sub:
            section_marker = SOUNDBAR_SECTION
        if not section_marker:
            skipped.append(code); continue
        # Find marker, insert after first product in that section
        idx = new_html.find(section_marker)
        if idx < 0:
            skipped.append(code); continue
        # Insert at end of the section (just before the next // ─── marker)
        next_marker = new_html.find('// ─', idx + len(section_marker))
        if next_marker < 0: next_marker = len(new_html)
        # Find a good insertion point: right before next_marker
        # Backtrack to last "}," before next_marker
        insert_at = new_html.rfind('},\n', idx, next_marker)
        if insert_at < 0:
            insert_at = next_marker
        else:
            insert_at += 2  # after the },
        new_html = new_html[:insert_at] + '\n' + entry + ',\n' + new_html[insert_at:]
        added.append(code)

print(f'Updated: {len(updated)}')
for c in updated: print(f'  U {c}')
print(f'Added: {len(added)}')
for c in added: print(f'  A {c}')
if skipped:
    print(f'Skipped: {len(skipped)}')
    for c in skipped: print(f'  S {c}')

with open(HTML_PATH,'w',encoding='utf-8') as f:
    f.write(new_html)
print(f'\nSize: {len(html):,} -> {len(new_html):,} ({len(new_html)-len(html):+,})')
