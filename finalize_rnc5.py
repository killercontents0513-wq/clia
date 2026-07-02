"""
RNC5 크롤 (v6_20 의 RNC5 항목 — XBOOM 파티 스피커로 수정)
- 기존: nm="TONE Free ANC Earbuds" (오류) → 실제: XBOOM Party Speaker
- 갤러리: D-01 + Z-01 + DZ-01~08 (10장) in /images/sound-bars/rnc5_dsauelk_emsj_sa_en_c/gallery/
- 피처: 6장 desktop /images/av/features/AV-XBOOM-RNC5-XX
- 스펙: c-compare-selling 11개
"""
import re, sys, io, struct, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

V6_20    = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
CODE     = 'RNC5'
CDN_BASE = 'https://www.lg.com/content/dam/channel/wcms/sa_en'

TOP_ORDER = ['SC9S', 'SH5A', 'RNC5', 'LSEL6333D', 'LT19HBHSIN', 'S90TR', 'S80TR', 'S45TR',
             '32GS95UV-B', 'WTV17HHD', '27US550-W', 'WK1310BST', 'RH10V9PV2W', 'WFV1214BST1']

# ── 갤러리: D-01 + Z-01 + DZ-01~08 (10장) ────────────────────────────────
GAL_BASE  = '/images/sound-bars/rnc5_dsauelk_emsj_sa_en_c/gallery/'
GAL_PATHS = [
    GAL_BASE + 'D-01.jpg',
    GAL_BASE + 'Z-01.jpg',
] + [GAL_BASE + f'DZ-{str(i).zfill(2)}.jpg' for i in range(1, 9)]

# ── 피처 (6장 Desktop — 실제 페이지 텍스트 기반) ─────────────────────────────
FEAT_BASE = '/images/av/features/'
FEAT_LIST = [
    (FEAT_BASE + 'AV-XBOOM-RNC5-01-Identity-Desktop.jpg',
     'XBOOM RNC5', 'LG XBOOM RNC5 — The All-in-One for Bold Party Sound',
     'LG XBOOM RNC5 packs powerful bass, DJ features, karaoke, and RGB lighting into one party-ready speaker.'),
    (FEAT_BASE + 'AV-XBOOM-RNC5-02-DoubleSuperBassBoost-Desktop.jpg',
     'Bass Blast+', 'Bass Blast+ — Big, Powerful Beats',
     'Super Bass Boost and Bass Blast+ deliver deep, powerful beats that elevate the party atmosphere up a notch.'),
    (FEAT_BASE + 'AV-XBOOM-RNC5-03-MultiColorLighting-Thumbnail-Desktop.jpg',
     'RGB Lighting', 'Multi Color (RGB) Speaker Lighting',
     'Multi Color RGB speaker lighting syncs with the music, creating a dynamic visual experience for every party.'),
    (FEAT_BASE + 'AV-XBOOM-RNC5-06-DJapp-Desktop.jpg',
     'DJ App', 'Sync Your Smartphone with the Beat',
     'Connect up to three smartphones and control DJ effects live from the LG XBOOM app on Android or iOS.'),
    (FEAT_BASE + 'AV-XBOOM-RNC5-07-Karaokestar-Desktop.jpg',
     'DJ Function', 'Spin the Decks from the Dance Floor',
     'Apply sound effects, loops, and scratches straight from the DJ Pad on the speaker or DJ App on your phone.'),
    (FEAT_BASE + 'AV-XBOOM-RNC5-08-Party-Saver-Desktop.jpg',
     'Karaoke', 'Sing It Loud and Clear — Karaoke Function',
     "Adjust mic and music volume separately, cancel track vocals with the Voice Canceller, and sing your heart out."),
]

# ── 스펙 ──────────────────────────────────────────────────────────────────
SPECS = {
    'Type':              'XBOOM Party Speaker',
    'Speaker_System':    '2-Way 3 Speaker (2" Tweeter x2, 8" Woofer)',
    'Bass_Blast_Plus':   'Yes',
    'RGB_Lighting':      'Multi Color (RGB)',
    'DJ_Function':       'Yes (DJ Pad / DJ App)',
    'Karaoke':           'Yes (Mic Input, Voice Canceller, Key Changer)',
    'Juke_Box':          'Yes',
    'Bluetooth':         '4.0 (Multi: up to 3 devices)',
    'USB_Input':         '2',
    'Guitar_Input':      '1 (6.3mm)',
    'Mic_Input':         '1 (6.3mm)',
    'EQ_Modes':          'Standard / Pop / Classic / Rock / Jazz / Bass Blast+ / Football',
    'Special_EQ':        'Arabic / Dangdut / Afro Hip-hop / India / Reggaeton + more',
    'Power_Supply':      '110-240V 50/60Hz (Wide)',
    'Dimension_mm':      '330 x 685 x 344',
    'Net_Weight_kg':     '13.8',
    'Model':             CODE,
}

# ── 유틸 ──────────────────────────────────────────────────────────────────
def jsstr(s):
    if s is None: s=''
    s=str(s).replace('™','TM').replace('®','R').replace("'''","'")
    s=s.replace('\\','\\\\').replace('"','\\"')
    return re.sub(r'\s+',' ',s.replace('\n',' ').replace('\r','').replace('\t',' ')).strip()

def image_dims(url, retries=3):
    for attempt in range(retries):
        try:
            req=urllib.request.Request(url,headers={'Range':'bytes=0-65536','User-Agent':'Mozilla/5.0'})
            data=urllib.request.urlopen(req,timeout=15).read()
            if data[:2]==b'\xff\xd8':
                i=2
                while i<len(data)-9:
                    if data[i]!=0xff: break
                    mk=data[i+1]; ln=struct.unpack('>H',data[i+2:i+4])[0]
                    if mk in(0xC0,0xC2):
                        return struct.unpack('>H',data[i+7:i+9])[0],struct.unpack('>H',data[i+5:i+7])[0]
                    i+=2+ln
            if data[:8]==b'\x89PNG\r\n\x1a\n':
                return struct.unpack('>II',data[16:24])
        except Exception:
            if attempt<retries-1: time.sleep(1)
    return 0,0

def replace_field(entry, field, new_val):
    pat=re.compile(r'(?<=[,{])\s*'+re.escape(field)+r'\s*:\s*(\[[\s\S]*?\]|\{[\s\S]*?\})',re.DOTALL)
    m=pat.search(entry)
    if not m: print(f'  WARNING: {field} not found'); return entry
    return entry[:m.start(1)]+new_val+entry[m.end(1):]

def replace_str_field(entry, field, new_val):
    pat=re.compile(r'(?<=[,{])'+re.escape(field)+r':"(?:[^"\\]|\\.)*"')
    m=pat.search(entry)
    if not m: print(f'  WARNING: str {field} not found'); return entry
    return entry[:m.start()]+f'{field}:"{new_val}"'+entry[m.end():]

# ── 치수 fetch ────────────────────────────────────────────────────────────
print('Fetching dimensions...')
all_paths=GAL_PATHS+[p for p,*_ in FEAT_LIST]
dims={}
for p in all_paths:
    url=CDN_BASE+p
    w,h=image_dims(url)
    dims[p]=(w,h)
    print(f'  {p.split("/")[-1]}: {w}x{h}')
    time.sleep(0.1)

# ── JS 빌드 ──────────────────────────────────────────────────────────────
print('\nBuilding JS...')
gal_parts=[f'{{a:"View {i}",p:"{p}",w:{dims.get(p,(0,0))[0]},h:{dims.get(p,(0,0))[1]}}}' for i,p in enumerate(GAL_PATHS,1)]
new_gal_js='['+','.join(gal_parts)+']'
feat_parts=[f'{{a:"{jsstr(a)}",p:"{p}",t:"{jsstr(t)}",d:"{jsstr(d)}",w:{dims.get(p,(0,0))[0]},h:{dims.get(p,(0,0))[1]}}}' for p,a,t,d in FEAT_LIST]
new_feat_js='['+','.join(feat_parts)+']'
sp_parts=[f'"{k}":"{jsstr(v)}"' for k,v in SPECS.items()]
new_sp_js='{'+','.join(sp_parts)+'}'
print(f'  gal:{len(gal_parts)} feat:{len(feat_parts)} sp:{len(sp_parts)}')

# ── v6_20 교체 ────────────────────────────────────────────────────────────
print(f'\nUpdating v6_20 ({CODE})...')
v620=open(V6_20,encoding='utf-8').read()
idx=v620.find(f'{{id:"{CODE}"')
if idx<0: print('ERROR: entry not found'); import sys; sys.exit(1)
nxt=v620.find('{id:"',idx+10)
entry_old=v620[idx:nxt]
print(f'  Old: {len(entry_old):,} chars')
entry_new=replace_field(entry_old,'gal',new_gal_js)
entry_new=replace_field(entry_new,'feat',new_feat_js)
entry_new=replace_field(entry_new,'sp',new_sp_js)
entry_new=replace_str_field(entry_new,'nm','LG XBOOM RNC5 Party Speaker with DJ & Karaoke')
entry_new=replace_str_field(entry_new,'pr','299')
entry_new=replace_str_field(entry_new,'url','https://www.lg.com/sa_en/speakers/party-speakers/rnc5/')
print(f'  New: {len(entry_new):,} chars')
v620_new=v620[:idx]+entry_new+v620[nxt:]
open(V6_20,'w',encoding='utf-8').write(v620_new)
print('  Saved.')

# ── 순서 재배치 ────────────────────────────────────────────────────────────
print('\nReordering...')
html2=open(V6_20,encoding='utf-8').read()
fi=html2.find('{id:"'); ao=html2.rfind('[',0,fi); ac=html2.find('];',fi)
before,after,body=html2[:ao+1],html2[ac:],html2[ao+1:ac]
splits=list(re.finditer(r'(?=\{id:")',body))
entries=[]
for i,m in enumerate(splits):
    s=m.start(); e=splits[i+1].start() if i+1<len(splits) else len(body)
    raw=body[s:e].rstrip(',\n '); cm=re.match(r'\{id:"([^"]+)"',raw)
    entries.append((cm.group(1) if cm else f'UNK_{i}',raw))
top_set=set(TOP_ORDER); code_map={c:e for c,e in entries}
new_entries=[(c,code_map[c]) for c in TOP_ORDER if c in code_map]+[(c,e) for c,e in entries if c not in top_set]
open(V6_20,'w',encoding='utf-8').write(before+'\n'+',\n'.join(e for _,e in new_entries)+'\n'+after)
print(f'  Top 5: {[c for c,_ in new_entries[:5]]}  Total: {len(new_entries)}')

# ── 검증 ──────────────────────────────────────────────────────────────────
v_final=open(V6_20,encoding='utf-8').read()
idx2=v_final.find(f'{{id:"{CODE}"'); nxt2=v_final.find('{id:"',idx2+10)
e=v_final[idx2:nxt2]
print(f'\n✅ {CODE} gal:{e[:e.find("feat:")].count("{a:\"View ")} feat:{e[e.find("feat:"):e.find(",sp:")].count("{a:\"")} size:{len(e):,}')
