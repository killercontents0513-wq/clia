import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_18.html','r',encoding='utf-8') as f:
    html=f.read()
for code in ['LT19CBBSIN','WTV24HHP','32GS95UV-B','27US550-W','65QNED93A6A','STAGE301','WFN1310BST']:
    m = re.search(r'\{id:"'+re.escape(code)+r'"[\s\S]*?kw:"[^"]*"\}', html)
    if m:
        s = m.group()
        # Count images
        gal_n = s.count(',p:"/') if 'gal:[' in s else 0
        # Parse gal + feat counts roughly
        gm = re.search(r'gal:\[(.*?)\],\s*\nfeat:', s, re.DOTALL)
        fm = re.search(r'feat:\[(.*?)\],\s*\nsp:', s, re.DOTALL)
        gal_count = gm.group(1).count('{a:') if gm else 0
        feat_count = fm.group(1).count('{a:') if fm else 0
        price_m = re.search(r'pr:"([^"]*)"', s)
        price = price_m.group(1) if price_m else ''
        name_m = re.search(r'nm:"([^"]*)"', s)
        print(f'{code:12s} gal={gal_count:2d} feat={feat_count:2d} pr={price:>12s}  name="{name_m.group(1)[:50] if name_m else ""}"')
