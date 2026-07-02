"""
WTV17HHD 마무리 패치
- 피처: 아이콘(greyIcon/redIcon) 제거, -D.jpg 메인 피처만
- 치수: 순차 fetch (Rate-limit 회피)
- 제품명 수정
- 핵심 스펙만 선별
- v6_20 교체
"""
import re, sys, io, struct, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

V6_20    = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
CODE     = 'WTV17HHD'
CDN_BASE = 'https://www.lg.com/content/dam/channel/wcms/sa_en'

# ── 확정 갤러리 (large\d+ 1600 크기) ──────────────────────────────────────
GAL_PATHS = [
    '/images/washing-machines/wtv17hhd/gallery/1600/large01.jpg',
    '/images/washing-machines/wtv17hhd/gallery/1600/large02.jpg',
    '/images/washing-machines/wtv17hhd/gallery/1600/large03.jpg',
    '/images/washing-machines/wtv17hhd/gallery/1600/large04.jpg',
    '/images/washing-machines/wtv17hhd/gallery/1600/large05.jpg',
    '/images/washing-machines/wtv17hhd/gallery/1600/large06.jpg',
    '/images/washing-machines/wtv17hhd/gallery/1600/large07.jpg',
    '/images/washing-machines/wtv17hhd/gallery/1600/large08.jpg',
    '/images/washing-machines/wtv17hhd/gallery/1600/large09.jpg',
    '/images/washing-machines/wtv17hhd/gallery/1600/large010.jpg',
    '/images/washing-machines/wtv17hhd/gallery/1600/large011.jpg',
    '/images/washing-machines/wtv17hhd/gallery/1600/large012.jpg',
    '/images/washing-machines/wtv17hhd/gallery/1600/large013.jpg',
]

# ── 확정 피처 (메인 -D.jpg / -D.png만, 아이콘 제외) ─────────────────────────
FEAT_LIST = [
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-01-1-AI-DD-D.jpg',
     'AI DD', 'Powerful & Fast 3D Wash',
     'AI DD technology detects the fabric type and load, optimizing the wash motion for the best care.'),
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-02-Smooth-Operation-D.jpg',
     'Smooth Operation', 'Powerful Waterfall and Jet Spray',
     'Powerful waterfall and jet spray ensure thorough and efficient cleaning every wash.'),
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-03-1-TurboWash-3D-D.jpg',
     'TurboWash 3D', 'Tub & Pulsator Scrub Spin',
     'TurboWash 3D combines powerful water spray and drum rotation for faster, deeper clean.'),
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-04-1-1-Power-Motion-D.jpg',
     'Power Motion', 'Power Motion',
     'Power Motion creates strong water currents to remove stubborn stains effectively.'),
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-04-1-2-TurboDrum-D.jpg',
     'TurboDrum', 'TurboDrum™',
     'TurboDrum creates powerful water currents for thorough penetration into every fiber.'),
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-04-1-3-Jet-Spray-D.jpg',
     'Jet Spray', 'An Optimal Way to Wash',
     'Jet Spray ensures water reaches every part of the load for optimal wash performance.'),
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-05-2-1-6Motion-Agitating-D.jpg',
     '6Motion — Agitating', '6Motion DD',
     'Agitating motion applies continuous drum movements for powerful cleaning.'),
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-05-2-2-6Motion-Swing-D.jpg',
     '6Motion — Swing', '6Motion DD',
     'Swing motion gently cares for delicate fabrics while still cleaning effectively.'),
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-06-1-Capacity-D.jpg',
     'Large Capacity', 'Same Size on the Outside, Bigger Capacity Inside',
     '17 kg large capacity lets you wash more in a single load, saving time and energy.'),
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-07-1-Allergy-Care-D.jpg',
     'Allergy Care Steam', 'Steam Away Allergens and Bacteria',
     'Steam function removes 99.9% of allergens and bacteria for a healthier wash.'),
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-08-1-Lint-Filter-D.jpg',
     'Lint Filter', 'A Larger Lint Filter Keeps Your Clothes Clean',
     'Large lint filter captures more lint and debris, keeping your clothes and drum clean.'),
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-09-1-Scent-D.jpg',
     'Full Stainless Steel Tub', 'Full Stainless Steel Tub & Lint Filter',
     'Full stainless steel tub is highly durable and resists odor buildup.'),
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-10-2-1-Voice-Control-D.jpg',
     'ThinQ Voice Control', 'Connect and Control from Anywhere',
     'ThinQ app lets you control and monitor your washer remotely via smartphone.'),
    ('/images/washing-machines/wtv17hhd/feature/WM-Vplus-LED-AI-DD-11-1-Inverter-DD-D.jpg',
     'Inverter Direct Drive', 'Long Lasting and High Reliability',
     'Inverter Direct Drive motor delivers superior durability with fewer moving parts.'),
]

# ── 핵심 스펙 ─────────────────────────────────────────────────────────────
SPECS = {
    'Type':                 'Top Load Washer',
    'Max_Wash_Capacity_kg': '17',
    'Body_Color':           'Middle Black',
    'Lid_Type':             'Tempered Glass',
    'Dimensions_WxHxD_mm':  '632 x 1040 x 670',
    'Height_Lid_Open_mm':   '1355',
    'Weight_kg':            '45.5',
    'AI_DD':                'Yes',
    'TurboWash_3D':         'No',
    'TurboDrum':            'Yes',
    'JetSpray':             'Yes',
    '6Motion_DD':           'Yes',
    'Steam':                'Yes',
    'Inverter_DirectDrive': 'Yes',
    'ThinQ_Wi_Fi':          'Yes',
    'Smart_Pairing':        'Yes',
    'Smart_Diagnosis':      'Yes',
    'Water_Level':          'Auto/Manual (10 Levels)',
    'Temp':                 'Cold / Warm / Hot',
    'Delay_Timer':          '3-19 hours',
    'Display_Type':         'LED + Hard Buttons',
    'Model':                CODE,
}

# ── 유틸 ────────────────────────────────────────────────────────────────
def jsstr(s):
    if s is None: s = ''
    s = str(s).replace('\u2122','TM').replace('\u00ae','R').replace('\u2019',"'")
    s = s.replace('\\','\\\\').replace('"','\\"')
    return re.sub(r'\s+',' ', s.replace('\n',' ').replace('\r','').replace('\t',' ')).strip()

def image_dims(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'Range':'bytes=0-65536','User-Agent':'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=15).read()
            if data[:2] == b'\xff\xd8':
                i = 2
                while i < len(data)-9:
                    if data[i] != 0xff: break
                    mk = data[i+1]; ln = struct.unpack('>H',data[i+2:i+4])[0]
                    if mk in (0xC0,0xC2):
                        return struct.unpack('>H',data[i+7:i+9])[0], struct.unpack('>H',data[i+5:i+7])[0]
                    i += 2+ln
            if data[:8] == b'\x89PNG\r\n\x1a\n':
                return struct.unpack('>II', data[16:24])
        except Exception as e:
            if attempt < retries-1:
                time.sleep(1)
    return 0, 0

def replace_field(entry, field, new_val):
    pat = re.compile(r'(?<=[,{])\s*'+re.escape(field)+r'\s*:\s*(\[[\s\S]*?\]|\{[\s\S]*?\})', re.DOTALL)
    m = pat.search(entry)
    if not m: print(f'  WARNING: {field} not found'); return entry
    return entry[:m.start(1)] + new_val + entry[m.end(1):]

def replace_str_field(entry, field, new_val):
    pat = re.compile(r'(?<=[,{])'+re.escape(field)+r':"(?:[^"\\]|\\.)*"')
    m = pat.search(entry)
    if not m: print(f'  WARNING: str {field} not found'); return entry
    return entry[:m.start()] + f'{field}:"{new_val}"' + entry[m.end():]

# ── 치수 순차 fetch ────────────────────────────────────────────────────
print('Fetching dimensions (sequential)...')
all_paths = GAL_PATHS + [p for p,*_ in FEAT_LIST]
dims = {}
for p in all_paths:
    url = CDN_BASE + p
    w, h = image_dims(url)
    dims[p] = (w, h)
    fn = p.split('/')[-1]
    print(f'  {fn}: {w}x{h}')
    time.sleep(0.1)  # 속도 제한

# ── JS 빌드 ──────────────────────────────────────────────────────────
print('\nBuilding JS...')

# 갤러리
gal_parts = []
for i, p in enumerate(GAL_PATHS, 1):
    w, h = dims.get(p, (0, 0))
    gal_parts.append(f'{{a:"View {i}",p:"{p}",w:{w},h:{h}}}')
new_gal_js = '[' + ','.join(gal_parts) + ']'
print(f'  gal: {len(gal_parts)}')

# 피처
feat_parts = []
for p, a, t, d in FEAT_LIST:
    w, h = dims.get(p, (0, 0))
    feat_parts.append(f'{{a:"{jsstr(a)}",p:"{p}",t:"{jsstr(t)}",d:"{jsstr(d)}",w:{w},h:{h}}}')
new_feat_js = '[' + ','.join(feat_parts) + ']'
print(f'  feat: {len(feat_parts)}')

# 스펙
sp_parts = [f'"{k}":"{jsstr(v)}"' for k, v in SPECS.items()]
new_sp_js = '{' + ','.join(sp_parts) + '}'
print(f'  sp: {len(sp_parts)}')

# ── v6_20 교체 ───────────────────────────────────────────────────────
print('\nUpdating v6_20...')
v620 = open(V6_20, encoding='utf-8').read()
idx  = v620.find(f'{{id:"{CODE}"')
if idx < 0: print('ERROR: entry not found!'); sys.exit(1)
nxt  = v620.find('{id:"', idx + 10)
entry_old = v620[idx:nxt]
print(f'  Old: {len(entry_old):,} chars')

CORRECT_NM = 'LG 17 kg Top Load Washing Machine with ThinQ & AI DD'
entry_new = replace_field(entry_old, 'gal', new_gal_js)
entry_new = replace_field(entry_new, 'feat', new_feat_js)
entry_new = replace_field(entry_new, 'sp', new_sp_js)
entry_new = replace_str_field(entry_new, 'nm', jsstr(CORRECT_NM))
entry_new = replace_str_field(entry_new, 'pr', '3499')

print(f'  New: {len(entry_new):,} chars')
v620_new = v620[:idx] + entry_new + v620[nxt:]
open(V6_20, 'w', encoding='utf-8').write(v620_new)
print('  Saved.')

# ── 최종 검증 ───────────────────────────────────────────────────────
v2   = open(V6_20, encoding='utf-8').read()
idx2 = v2.find(f'{{id:"{CODE}"')
nxt2 = v2.find('{id:"', idx2 + 10)
e    = v2[idx2:nxt2]
nm_m = re.search(r'nm:"((?:[^"\\]|\\.)*)"', e)
pr_m = re.search(r',pr:"([^"]*)"', e)
gal_c  = e[:e.find('feat:')].count('{a:"View ')
feat_c = e[e.find('feat:'):e.find(',sp:')].count('{a:"')
sp_c   = e[e.find(',sp:'):e.find('},tags')].count('":"')
print(f'\n=== 최종 확인 ===')
print(f'  nm  : {nm_m.group(1) if nm_m else "?"}')
print(f'  pr  : {pr_m.group(1) if pr_m else "?"}')
print(f'  gal : {gal_c}장')
print(f'  feat: {feat_c}장')
print(f'  sp  : {sp_c}개')
print(f'  size: {len(e):,} chars')
print(f'\n✅ {CODE} 완료!')
