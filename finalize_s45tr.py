"""
S45TR 마무리 패치
- 갤러리: 2010-01~10 (10장), View N 라벨 + w/h
- 피처: 핵심 8장 (desktop -d.jpg)
- 스펙: 4.1ch 사운드바 핵심 스펙
- 순차 fetch (Rate-limit 회피)
"""
import re, sys, io, struct, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

V6_20    = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
CODE     = 'S45TR'
CDN_BASE = 'https://www.lg.com/content/dam/channel/wcms/sa_en'

TOP_ORDER = ['S80TR', 'S45TR', '32GS95UV-B', 'WTV17HHD', '27US550-W', 'WK1310BST', 'RH10V9PV2W', 'WFV1214BST1']

# ── 갤러리 (10장) ─────────────────────────────────────────────────────
BASE_G = '/speakers/soundbars/s45tr/gallery/'
GAL_PATHS = [BASE_G + f'2010-{str(i).zfill(2)}.jpg' for i in range(1, 11)]

# ── 핵심 피처 8장 ──────────────────────────────────────────────────────
BASE_F = '/speakers/soundbars/s45tr/features/'
FEAT_LIST = [
    (BASE_F + 'av-soundbar-s45tr-01-kv-d-1.jpg',
     'S45TR Soundbar', 'Powerful 4.1ch Surround Sound',
     'The LG S45TR delivers immersive 4.1ch surround sound with 400W total output power.'),
    (BASE_F + 'av-soundbar-s45tr-02-summary-d-v2.jpg',
     'Feature Overview', 'More Sound. More Ways to Enjoy.',
     'AI Sound Pro, wireless rear speakers and HDMI ARC all packed into a sleek soundbar.'),
    (BASE_F + 'av-soundbar-s45tr-03-perfect-match-d.jpg',
     'Perfect Match', 'Perfect Match for LG TV',
     'WOW Interface lets you control the soundbar directly from your LG TV remote.'),
    (BASE_F + 'av-soundbar-s45tr-04-surround-sound-d.jpg',
     '4.1ch Surround', 'Fill the Room with Sound',
     '4.1 channel surround sound wraps you in audio from every direction for a cinematic feel.'),
    ('/s45tr/gp1/features/desktop/soundbar-s45tr-2024-feature-05-1-rear-speakers.jpg',
     'Wireless Rear Speakers', 'Truly Wireless Rear Speakers Included',
     'Wireless rear speakers are included in the box for effortless true surround sound setup.'),
    (BASE_F + 'av-soundbar-s45tr-06-ai-sound-pro-d-1.jpg',
     'AI Sound Pro', 'AI Sound Pro',
     'AI Sound Pro automatically analyzes and optimizes audio for the content you are watching.'),
    (BASE_F + 'av-soundbar-s45tr-07-recycled-inside-d.jpg',
     'Recycled Materials', 'Sustainable Inside',
     'Internal components use recycled materials as part of LG\'s commitment to sustainability.'),
    (BASE_F + 'av-soundbar-s45tr-08-recycled-outside-d.jpg',
     'Recycled Packaging', 'Sustainable Outside',
     'Outer packaging made with recycled and eco-friendly materials to reduce environmental impact.'),
]

# ── 핵심 스펙 ──────────────────────────────────────────────────────────
SPECS = {
    'Type':               'Soundbar',
    'Channels':           '4.1ch',
    'Total_Output_W':     '400',
    'Dolby':              'Dolby Digital',
    'DTS':                'DTS Digital Surround',
    'AI_Sound_Pro':       'Yes',
    'Rear_Speakers':      'Yes (Wireless, Included)',
    'Bluetooth':          '5.3 (SBC/AAC)',
    'HDMI_ARC':           'Yes (1x)',
    'Optical':            'Yes (1x)',
    'USB':                'Yes (1x)',
    'WOW_Interface':      'Yes',
    'App_Control':        'Yes (iOS/Android)',
    'Soundbar_Dim_mm':    '720 x 63 x 87',
    'Subwoofer_Dim_mm':   '171 x 320 x 252',
    'Soundbar_Weight_kg': '1.65',
    'Color':              'Black',
    'Model':              CODE,
}

# ── 유틸 ───────────────────────────────────────────────────────────────
def jsstr(s):
    if s is None: s = ''
    s = str(s).replace('\u2122', 'TM').replace('\u00ae', 'R').replace('\u2019', "'")
    s = s.replace('\\', '\\\\').replace('"', '\\"')
    return re.sub(r'\s+', ' ', s.replace('\n', ' ').replace('\r', '').replace('\t', ' ')).strip()

def image_dims(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'Range': 'bytes=0-65536', 'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=15).read()
            if data[:2] == b'\xff\xd8':
                i = 2
                while i < len(data) - 9:
                    if data[i] != 0xff: break
                    mk = data[i+1]; ln = struct.unpack('>H', data[i+2:i+4])[0]
                    if mk in (0xC0, 0xC2):
                        return struct.unpack('>H', data[i+7:i+9])[0], struct.unpack('>H', data[i+5:i+7])[0]
                    i += 2 + ln
            if data[:8] == b'\x89PNG\r\n\x1a\n':
                return struct.unpack('>II', data[16:24])
        except Exception:
            if attempt < retries - 1:
                time.sleep(1)
    return 0, 0

def replace_field(entry, field, new_val):
    pat = re.compile(r'(?<=[,{])\s*' + re.escape(field) + r'\s*:\s*(\[[\s\S]*?\]|\{[\s\S]*?\})', re.DOTALL)
    m = pat.search(entry)
    if not m: print(f'  WARNING: {field} not found'); return entry
    return entry[:m.start(1)] + new_val + entry[m.end(1):]

def replace_str_field(entry, field, new_val):
    pat = re.compile(r'(?<=[,{])' + re.escape(field) + r':"(?:[^"\\]|\\.)*"')
    m = pat.search(entry)
    if not m: print(f'  WARNING: str {field} not found'); return entry
    return entry[:m.start()] + f'{field}:"{new_val}"' + entry[m.end():]

# ── 치수 순차 fetch ────────────────────────────────────────────────────
print('Fetching dimensions (sequential)...')
all_paths = GAL_PATHS + [p for p, *_ in FEAT_LIST]
dims = {}
for p in all_paths:
    url = CDN_BASE + p
    w, h = image_dims(url)
    dims[p] = (w, h)
    print(f'  {p.split("/")[-1]}: {w}x{h}')
    time.sleep(0.1)

# ── JS 빌드 ───────────────────────────────────────────────────────────
print('\nBuilding JS...')
gal_parts = [f'{{a:"View {i}",p:"{p}",w:{dims.get(p,(0,0))[0]},h:{dims.get(p,(0,0))[1]}}}'
             for i, p in enumerate(GAL_PATHS, 1)]
new_gal_js = '[' + ','.join(gal_parts) + ']'

feat_parts = [f'{{a:"{jsstr(a)}",p:"{p}",t:"{jsstr(t)}",d:"{jsstr(d)}",w:{dims.get(p,(0,0))[0]},h:{dims.get(p,(0,0))[1]}}}'
              for p, a, t, d in FEAT_LIST]
new_feat_js = '[' + ','.join(feat_parts) + ']'

sp_parts = [f'"{k}":"{jsstr(v)}"' for k, v in SPECS.items()]
new_sp_js = '{' + ','.join(sp_parts) + '}'

print(f'  gal: {len(gal_parts)}, feat: {len(feat_parts)}, sp: {len(sp_parts)}')

# ── v6_20 교체 ────────────────────────────────────────────────────────
print('\nUpdating v6_20...')
v620 = open(V6_20, encoding='utf-8').read()
idx = v620.find(f'{{id:"{CODE}"')
if idx < 0: print('ERROR: entry not found!'); sys.exit(1)
nxt = v620.find('{id:"', idx + 10)
entry_old = v620[idx:nxt]
print(f'  Old: {len(entry_old):,} chars')

entry_new = replace_field(entry_old, 'gal', new_gal_js)
entry_new = replace_field(entry_new, 'feat', new_feat_js)
entry_new = replace_field(entry_new, 'sp', new_sp_js)
entry_new = replace_str_field(entry_new, 'nm', 'LG S45TR 4.1ch Soundbar with Wireless Rear Speakers')
entry_new = replace_str_field(entry_new, 'pr', '549')

print(f'  New: {len(entry_new):,} chars')
v620_new = v620[:idx] + entry_new + v620[nxt:]
open(V6_20, 'w', encoding='utf-8').write(v620_new)
print('  Saved.')

# ── 순서 재배치 ────────────────────────────────────────────────────────
print('\nReordering...')
html2 = open(V6_20, encoding='utf-8').read()
fi = html2.find('{id:"')
ao = html2.rfind('[', 0, fi)
ac = html2.find('];', fi)
before, after, body = html2[:ao+1], html2[ac:], html2[ao+1:ac]
splits = list(re.finditer(r'(?=\{id:")', body))
entries = []
for i, m in enumerate(splits):
    s = m.start()
    e = splits[i+1].start() if i+1 < len(splits) else len(body)
    raw = body[s:e].rstrip(',\n ')
    cm = re.match(r'\{id:"([^"]+)"', raw)
    entries.append((cm.group(1) if cm else f'UNK_{i}', raw))
top_set = set(TOP_ORDER)
code_map = {c: e for c, e in entries}
new_entries = [(c, code_map[c]) for c in TOP_ORDER if c in code_map] + \
              [(c, e) for c, e in entries if c not in top_set]
open(V6_20, 'w', encoding='utf-8').write(before + '\n' + ',\n'.join(e for _, e in new_entries) + '\n' + after)
print(f'  Top 5: {[c for c, _ in new_entries[:5]]}')
print(f'  Total: {len(new_entries)}')

# ── 최종 검증 ─────────────────────────────────────────────────────────
v_final = open(V6_20, encoding='utf-8').read()
idx2 = v_final.find(f'{{id:"{CODE}"')
nxt2 = v_final.find('{id:"', idx2 + 10)
e = v_final[idx2:nxt2]
gal_c  = e[:e.find('feat:')].count('{a:"View ')
feat_c = e[e.find('feat:'):e.find(',sp:')].count('{a:"')
print(f'\n=== 최종 확인 ===')
print(f'  gal : {gal_c}장')
print(f'  feat: {feat_c}장')
print(f'  size: {len(e):,} chars')
print(f'\n✅ {CODE} 완료!')
