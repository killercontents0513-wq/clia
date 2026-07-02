"""Patch RH81T2SP7RM features in bulk_data.json with composite imgs[] grouping."""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'

with open(f'{BASE}/bulk_data.json', 'r', encoding='utf-8') as f:
    bulk = json.load(f)

rh81 = next(p for p in bulk if p['code'] == 'RH81T2SP7RM')

# Current 6 features:
# [0] 01-intro-d         1600x1450  — single hero
# [1] 02-2-1-heater-d    800x700    \__ composite pair (2 images)
# [2] 02-2-2-heatpump-d  800x700    /
# [3] 05-2-1-washer-d    521x750    \
# [4] 05-2-2-door-d      739x363     >-- composite trio (3 images)
# [5] 05-2-3-control-d   739x363    /

feats = rh81['features']
print('Current features:')
for i,ft in enumerate(feats):
    print(f'  [{i}] {ft["p"].split("/")[-1]:55s} {ft.get("w","?")}x{ft.get("h","?")}')

# Build composite structure
new_features = [
    # 1) Single hero — intro
    feats[0],

    # 2) Composite: heater vs heatpump (2 images)
    {
        'a': 'Heater Dryer vs Heat Pump',
        'p': feats[1]['p'],   # primary = first sub-image
        't': feats[1]['t'],   # "Enjoy the Gentle Dry with Heat Pump"
        'd': feats[1]['d'],
        'w': feats[1].get('w', 800),
        'h': feats[1].get('h', 700),
        'imgs': [
            {'a': feats[1]['a'], 'p': feats[1]['p'],
             'w': feats[1].get('w',800), 'h': feats[1].get('h',700)},
            {'a': feats[2]['a'], 'p': feats[2]['p'],
             'w': feats[2].get('w',800), 'h': feats[2].get('h',700)},
        ]
    },

    # 3) Composite: design details trio (3 images)
    {
        'a': 'Visible and Elegant Design',
        'p': feats[3]['p'],   # primary = first sub-image
        't': feats[3]['t'],   # "Visible and Elegant Design"
        'd': feats[3]['d'],
        'w': feats[3].get('w', 521),
        'h': feats[3].get('h', 750),
        'imgs': [
            {'a': feats[3]['a'], 'p': feats[3]['p'],
             'w': feats[3].get('w',521), 'h': feats[3].get('h',750)},
            {'a': feats[4]['a'], 'p': feats[4]['p'],
             'w': feats[4].get('w',739), 'h': feats[4].get('h',363)},
            {'a': feats[5]['a'], 'p': feats[5]['p'],
             'w': feats[5].get('w',739), 'h': feats[5].get('h',363)},
        ]
    },
]

rh81['features'] = new_features

with open(f'{BASE}/bulk_data.json', 'w', encoding='utf-8') as f:
    json.dump(bulk, f, ensure_ascii=False, indent=1)

print('\nPatched features:')
for i,ft in enumerate(new_features):
    n = len(ft.get('imgs',[])) if ft.get('imgs') else 1
    print(f'  [{i}] {"COMPOSITE("+str(n)+")" if ft.get("imgs") else "single":15s} {ft["t"][:50]:50s}')
    if ft.get('imgs'):
        for im in ft['imgs']:
            print(f'       > {im["p"].split("/")[-1]}: {im.get("w","?")}x{im.get("h","?")}')

print('\nbulk_data.json patched.')
