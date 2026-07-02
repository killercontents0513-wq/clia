import re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

HTML = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
CODE = 'BUDS-BK'

with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/buds_bk_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

specs = data['sp']
print(f'Specs: {len(specs)}')

# Price formatting
try:
    n = float(data['pr'].replace(',', ''))
    pr_str = f"SAR {int(round(n)):,}"
except:
    pr_str = f"SAR {data['pr']}" if data['pr'] else 'SAR 249'
print(f'Price: {pr_str}')

def js_str(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').strip()

gal_js = ',\n'.join(
    '{' + f'a:"{js_str(g["a"])}",p:"{g["p"]}"' + '}' for g in data['gal'])

feat_js = ',\n'.join(
    '{' + f'a:"{js_str(f["a"])}",p:"{f["p"]}",t:"{js_str(f["t"])}",d:""' + '}' for f in data['feat'])

sp_js = '{' + ','.join(f'"{k}":"{js_str(v)}"' for k, v in specs.items()) + '}'

new_entry = (
    '{' + f'id:"{CODE}",dv:"Audio",cat:"Audio",sub:"Wireless Earbuds",ico:"🎧",'
    f'nm:"{js_str(data["nm"])}",'
    f'pr:"{pr_str}",op:"",'
    f'url:"https://www.lg.com/sa_en/wireless-earbuds/xboombuds/buds-bk/",'
    f'crawled:true,\n'
    f'gal:[\n{gal_js}\n],\n'
    f'feat:[\n{feat_js}\n],\n'
    f'sp:{sp_js},'
    f'tags:["XBOOM","ANC","Auracast","Bluetooth 5.3"],'
    f'bul:[],faq:[],\n'
    f'promo:[{{icon:"Free Delivery",tip:"Free delivery across KSA"}},{{icon:"5% Welcome Discount",tip:"5% off for LG Members"}}],\n'
    f'disc:["All images and specs from LG.com Saudi Arabia.","Features and availability may vary by region."],\n'
    f'kw:"LG XBOOM Buds Wireless Earbuds ANC Auracast Bluetooth 5.3 Saudi Arabia KSA"' + '}'
)

print(f'Entry length: {len(new_entry):,} chars')

# Backup + Inject
shutil.copy(HTML, HTML.replace('.html', '.pre_buds_bk.html'))

with open(HTML, 'r', encoding='utf-8') as f:
    html_main = f.read()

if f'id:"{CODE}"' in html_main:
    print(f'{CODE} already exists — removing old entry')
    s = html_main.find(f'{{id:"{CODE}"')
    e = html_main.find('{id:"', s + 10)
    html_main = html_main[:s] + html_main[e:]

p_array_start = html_main.find('const P=[')
insert_pos = p_array_start + len('const P=[')
html_main = html_main[:insert_pos] + new_entry + ',\n' + html_main[insert_pos:]

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html_main)

print('Saved.')

with open(HTML, 'r', encoding='utf-8') as f:
    v = f.read()
pos = v.find('const P=[')
first_id = re.search(r'id:"([^"]+)"', v[pos:pos+100])
print(f'First product in P[]: {first_id.group(1) if first_id else "?"}')
print(f'{CODE} present: {CODE in v}')
