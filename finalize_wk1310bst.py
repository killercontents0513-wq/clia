"""WK1310BST 최종 마무리: 피처 레이블 + 스펙 보강"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

V6_20 = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'

def jsstr(s):
    if s is None: s = ''
    s = str(s).replace('\u2122', 'TM').replace('\u00ae', 'R')
    s = s.replace('\\', '\\\\').replace('"', '\\"')
    return re.sub(r'\s+', ' ', s.replace('\n', ' ').replace('\r', '').replace('\t', ' ')).strip()

# 스펙 (HTML 추출 4개 + 제품명 기반 보강)
SPECS = {
    'Type':                      'WashTower (Washer + Dryer)',
    'Max_Wash_Capacity_kg':      '13',
    'Max_Dry_Capacity_kg':       '10',
    'Body_Color':                'Black Steel',
    'Product_Dimensions_mm':     '600 x 1650 x 660',
    'ThinQ_Wi_Fi':               'Yes',
    'Inverter_DirectDrive':      'Yes',
    'Centre_Control':            'Yes',
    'AI_DD':                     'Yes',
    'Steam':                     'Yes',
    'TurboWash':                 'Yes',
    'Model':                     'WK1310BST',
}

# 피처 레이블 (순서 유지)
LABELS = [
    'WashTower Intro',
    'Centre Control 1',
    'Space Saving',
    'Fabric Care AI',
    'Time Saving',
    'Black Steel Design',
    'Auto Sense AI DD',
    'Synced Cycles',
    'AI Intelligence',
    'Wash & Dry 1hr',
    'TurboWash 39min',
    'ThinQ Smart Control',
    'Smart Pairing',
    'Efficient Maintenance',
    'Allergy Care Washer',
    'Allergy Care Dryer',
]

v620 = open(V6_20, encoding='utf-8').read()
idx  = v620.find('{id:"WK1310BST"')
nxt  = v620.find('{id:"', idx + 10)
entry = v620[idx:nxt]

# feat 아이템 파싱 후 레이블만 교체
feat_items = re.findall(
    r'\{a:"[^"]*",p:"([^"]*)",t:"([^"]*)",d:"([^"]*)",w:(\d+),h:(\d+)\}', entry)
print(f'Feature items found: {len(feat_items)}')

new_feat_parts = []
for i, (p, t, d, w, h) in enumerate(feat_items):
    label = LABELS[i] if i < len(LABELS) else f'Feature {i+1}'
    new_feat_parts.append(
        f'{{a:"{jsstr(label)}",p:"{p}",t:"{t}",d:"{d}",w:{w},h:{h}}}')
new_feat_js = '[' + ','.join(new_feat_parts) + ']'

# 스펙 JS
sp_parts = [f'"{k}":"{jsstr(v)}"' for k, v in SPECS.items()]
new_sp_js = '{' + ','.join(sp_parts) + '}'

def replace_field(entry, field, new_val):
    pat = re.compile(
        r'(?<=[,{])\s*' + re.escape(field) + r'\s*:\s*(\[[\s\S]*?\]|\{[\s\S]*?\})',
        re.DOTALL)
    m = pat.search(entry)
    if not m:
        print(f'WARNING: {field} not found'); return entry
    return entry[:m.start(1)] + new_val + entry[m.end(1):]

entry_new = replace_field(entry, 'feat', new_feat_js)
entry_new = replace_field(entry_new, 'sp', new_sp_js)

v620_new = v620[:idx] + entry_new + v620[nxt:]
open(V6_20, 'w', encoding='utf-8').write(v620_new)

print(f'Entry: {len(entry):,} -> {len(entry_new):,} chars')
print(f'Specs: {len(SPECS)} items')
print('Labels:', LABELS)
print('\n✅ WK1310BST finalized!')
