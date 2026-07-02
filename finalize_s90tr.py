"""
S90TR 마무리 패치
- 갤러리: gallery-zoom 01~11 (11장)
- 피처: 핵심 12장 (desktop)
- 스펙: 7.1.3ch 사운드바 핵심 스펙
- 순차 fetch (Rate-limit 회피)
"""
import re, sys, io, struct, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

V6_20    = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
CODE     = 'S90TR'
CDN_BASE = 'https://www.lg.com/content/dam/channel/wcms/sa_en'

TOP_ORDER = ['LSEL6333D', 'LT19HBHSIN', 'S90TR', 'S80TR', 'S45TR', '32GS95UV-B', 'WTV17HHD', '27US550-W', 'WK1310BST', 'RH10V9PV2W', 'WFV1214BST1']

# ── 갤러리 (gallery-zoom 11장) ─────────────────────────────────────────
BASE_G = '/speakers/soundbars/s90tr/features/gallery/'
GAL_PATHS = [BASE_G + f'av-soundbar-s90tr-gallery-zoom-{str(i).zfill(2)}.jpg' for i in range(1, 12)]

# ── 핵심 피처 12장 ─────────────────────────────────────────────────────
BASE_F = '/speakers/soundbars/s90tr/features/'
FEAT_LIST = [
    (BASE_F + 'av-soundbar-s90tr-01-kv-d.jpg',
     'S90TR Soundbar', '7.1.3ch Soundbar with Dolby Atmos',
     'The LG S90TR delivers 7.1.3ch Dolby Atmos surround sound with 670W total output power.'),
    (BASE_F + 'av-soundbar-s90tr-02-summary-d-v2.jpg',
     'Feature Overview', 'Premium Sound. Complete System.',
     'AI Room Calibration Pro, WOWCAST, AirPlay 2 and Chromecast — everything you need.'),
    (BASE_F + 'av-soundbar-s90tr-03-center-up-firing-channel-d.jpg',
     'Center Up-Firing', 'Center Up-Firing Channel',
     'A dedicated center up-firing channel creates a wider, more spacious soundstage above you.'),
    (BASE_F + 'av-soundbar-s90tr-04-triple-level-spatial-sound-d.jpg',
     'Triple Level Sound', 'Triple Level Spatial Sound',
     'Three levels — front, surround and height — place sound precisely in every direction.'),
    (BASE_F + 'av-soundbar-s90tr-05-surround-sound-d-v2.jpg',
     '7.1.3ch Surround', '7.1.3ch Full Surround System',
     'With front, center, surround and height channels, every seat is the best seat in the house.'),
    ('/s90tr/gp1/features/desktop/soundbar-s90tr-2024-feature-06-1-rear-speakers.jpg',
     'Wireless Rear Speakers', 'Wireless Rear Speakers Included',
     'High-performance wireless rear speakers come in the box for instant true surround sound.'),
    (BASE_F + 'av-soundbar-s90tr-07-perfect-match-d-1-01-v2.jpg',
     'Perfect Match', 'Perfect Match for LG TV',
     'WOWCAST delivers lossless wireless multi-channel audio direct from your LG TV.'),
    (BASE_F + 'av-soundbar-s90tr-08-ai-room-calibration-pro-d-1-v2.jpg',
     'AI Room Calibration Pro', 'AI Room Calibration Pro',
     'AI Room Calibration Pro automatically optimizes audio based on your room\'s acoustics.'),
    (BASE_F + 'av-soundbar-s90tr-09-multi-channel-audio-experience-d-3-v2.jpg',
     'Multi-Channel Upscaling', 'Multi-Channel Audio Experience',
     'AI upscales any stereo or 5.1 content to full multi-channel audio in real time.'),
    (BASE_F + 'av-soundbar-s90tr-10-ai-sound-pro-d.jpg',
     'AI Sound Pro', 'AI Sound Pro',
     'AI Sound Pro analyzes content and automatically optimizes the sound profile for it.'),
    (BASE_F + 'av-soundbar-s90tr-11-intense-gaming-d-1.jpg',
     'Gaming Mode', 'Intense Gaming Audio',
     'HDMI 2.1 with VRR and ALLM and a dedicated Game Mode for the ultimate gaming audio.'),
    (BASE_F + 'av-soundbar-s90tr-17-dolby-atmos-d.jpg',
     'Dolby Atmos & DTS:X', 'Dolby Atmos and DTS:X Certified',
     'Full Dolby Atmos and DTS:X decoding delivers object-based 3D surround sound.'),
]

# ── 핵심 스펙 ──────────────────────────────────────────────────────────
SPECS = {
    'Type':                    'Soundbar',
    'Channels':                '7.1.3ch',
    'Total_Output_W':          '670',
    'Dolby_Atmos':             'Yes',
    'DTS_X':                   'Yes',
    'AI_Room_Calibration_Pro': 'Yes',
    'AI_Sound_Pro':            'Yes',
    'Rear_Speakers':           'Yes (Wireless, Included)',
    'Center_Up_Firing':        'Yes',
    'HDMI':                    'HDMI 2.1 eARC (VRR/ALLM)',
    'AirPlay_2':               'Yes',
    'Chromecast':              'Yes',
    'Spotify_Connect':         'Yes',
    'TIDAL_Connect':           'Yes',
    'WOWCAST':                 'Yes (Lossless LG TV Link)',
    'WOW_Interface':           'Yes',
    'Color':                   'Black',
    'Model':                   CODE,
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
            if attempt < retries - 1: time.sleep(1)
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
print('Fetching dimensions...')
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
print(f'  gal:{len(gal_parts)} feat:{len(feat_parts)} sp:{len(sp_parts)}')

# ── v6_20 교체 ────────────────────────────────────────────────────────
print('\nUpdating v6_20...')
v620 = open(V6_20, encoding='utf-8').read()
idx = v620.find(f'{{id:"{CODE}"')
if idx < 0: print('ERROR'); sys.exit(1)
nxt = v620.find('{id:"', idx + 10)
entry_old = v620[idx:nxt]
print(f'  Old: {len(entry_old):,} chars')
entry_new = replace_field(entry_old, 'gal', new_gal_js)
entry_new = replace_field(entry_new, 'feat', new_feat_js)
entry_new = replace_field(entry_new, 'sp', new_sp_js)
entry_new = replace_str_field(entry_new, 'nm', 'LG S90TR 7.1.3ch Soundbar with Dolby Atmos')
entry_new = replace_str_field(entry_new, 'pr', '2199')
print(f'  New: {len(entry_new):,} chars')
v620_new = v620[:idx] + entry_new + v620[nxt:]
open(V6_20, 'w', encoding='utf-8').write(v620_new)
print('  Saved.')

# ── 순서 재배치 ────────────────────────────────────────────────────────
print('\nReordering...')
html2 = open(V6_20, encoding='utf-8').read()
fi = html2.find('{id:"'); ao = html2.rfind('[', 0, fi); ac = html2.find('];', fi)
before, after, body = html2[:ao+1], html2[ac:], html2[ao+1:ac]
splits = list(re.finditer(r'(?=\{id:")', body))
entries = []
for i, m in enumerate(splits):
    s = m.start(); e = splits[i+1].start() if i+1 < len(splits) else len(body)
    raw = body[s:e].rstrip(',\n '); cm = re.match(r'\{id:"([^"]+)"', raw)
    entries.append((cm.group(1) if cm else f'UNK_{i}', raw))
top_set = set(TOP_ORDER); code_map = {c: e for c, e in entries}
new_entries = [(c, code_map[c]) for c in TOP_ORDER if c in code_map] + [(c, e) for c, e in entries if c not in top_set]
open(V6_20, 'w', encoding='utf-8').write(before + '\n' + ',\n'.join(e for _, e in new_entries) + '\n' + after)
print(f'  Top 5: {[c for c, _ in new_entries[:5]]}  Total: {len(new_entries)}')

# ── 검증 ─────────────────────────────────────────────────────────────
v_final = open(V6_20, encoding='utf-8').read()
idx2 = v_final.find(f'{{id:"{CODE}"'); nxt2 = v_final.find('{id:"', idx2+10)
e = v_final[idx2:nxt2]
print(f'\n✅ {CODE} gal:{e[:e.find("feat:")].count("{a:\"View ")} feat:{e[e.find("feat:"):e.find(",sp:")].count("{a:\"")} size:{len(e):,}')
