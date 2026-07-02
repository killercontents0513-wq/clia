import re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/wfr_ordered.json','r',encoding='utf-8') as f:
    D=json.load(f)
print('=== WFR1114WH — full PDP dump ===')
print(f'Name: {D["name"]}')
print(f'Price: SAR {D["price"]}')
print(f'\nGallery ({len(D["gallery"])} images in PDP HTML order):')
for i, g in enumerate(D['gallery']):
    print(f'  {i+1:2d}. {g["w"]:4d}x{g["h"]:4d}  [{g["a"]:>12s}]  {g["file"][:55]}')
print(f'\nFeatures ({len(D["features"])} images in PDP HTML order):')
for i, f in enumerate(D['features']):
    variant = 'desktop' if 'desktop' in f['file'].lower() or '-d.' in f['file'].lower() else ('mobile' if 'mobile' in f['file'].lower() or '-m.' in f['file'].lower() else 'other')
    print(f'  {i+1:2d}. {f["w"]:4d}x{f["h"]:4d}  [{variant:>7s}]  t="{f["t"][:40]}"  {f["file"][:55]}')
print(f'\nSpecs: {len(D["specs"])}')
for k,v in list(D['specs'].items())[:5]:
    print(f'  {k} = {v[:80]}')
