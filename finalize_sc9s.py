"""
SC9S 크롤 (v6_20 의 SC95 항목 수정)
- id: SC95 → SC9S (코드 오타 수정)
- 갤러리: large01~07 (7장) in /images/sound-bars/sc9s_dsauelk_emsj_sa_en_c/gallery/
- 피처: 6장 desktop (av/features + tvs-soundbars + feature 폴더)
- 스펙: c-compare-selling 핵심 20개
"""
import re, sys, io, struct, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

V6_20    = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
OLD_CODE = 'SC95'   # v6_20 에 등록된 코드 (오타)
NEW_CODE = 'SC9S'   # 실제 LG SA 코드
CDN_BASE = 'https://www.lg.com/content/dam/channel/wcms/sa_en'

TOP_ORDER = ['SC9S', 'SH5A', 'RNC5', 'LSEL6333D', 'LT19HBHSIN', 'S90TR', 'S80TR', 'S45TR',
             '32GS95UV-B', 'WTV17HHD', '27US550-W', 'WK1310BST', 'RH10V9PV2W', 'WFV1214BST1']

# ── 갤러리: large01~07 ────────────────────────────────────────────────────
GAL_BASE  = '/images/sound-bars/sc9s_dsauelk_emsj_sa_en_c/gallery/'
GAL_PATHS = [GAL_BASE + f'large{str(i).zfill(2)}.jpg' for i in range(1, 8)]

# ── 피처 (6장 Desktop) ───────────────────────────────────────────────────
FEAT_LIST = [
    ('/tvs-soundbars/soundbars/av-soundbar-sc9s-features-2023/desktop/AV-SoundBar-SC9S-02-3-Synergy-Desktop.jpg',
     'WOW Orchestra', 'WOW Orchestra — LG TV & Soundbar Synergy',
     'WOW Orchestra syncs your LG TV speakers and soundbar for a richer, optimized surround sound experience.'),
    ('/images/av/features/D10_AV-SoundBar-SC9S-03-3-Advanced-Sound-Experience-Desktop.jpg',
     'Dolby Atmos', "World's 1st Dolby Atmos Soundbar with Triple Up-firing Channels",
     "Meet the World's First Triple Up-firing Channels. LG SC9S delivers wider and more immersive 3D sound from above."),
    ('/feature/soundbar-sc9s-2023-03-1-advanced-sound-experience-desktop.jpg',
     'Theater Sound', 'Experience Theater Quality Sound — Dolby Atmos & DTS:X',
     'LG Soundbar combines Dolby Atmos and DTS:X to bring theater-like 3D sound to your living room.'),
    ('/images/av/features/D21_AV-SoundBar-SC9S-05-4-Smart-Function-Desktop.jpg',
     'WOW Interface', 'WOW Interface & 4K Pass-Through for Seamless Setup',
     'WOW Interface simplifies home theater setup; 4K Pass-Through with VRR/ALLM supports next-gen gaming.'),
    ('/images/av/features/D22_AV-SoundBar-SC9S-05-6-Smart-Function-Desktop.jpg',
     'WOW Bracket', 'WOW Bracket — Perfect Match for LG OLED C Series TV',
     'The WOW Bracket cable management system aligns and mounts seamlessly with LG OLED C Series TVs.'),
    ('/images/av/features/D24_AV-SoundBar-SC9S-05-8-Smart-Function-Desktop.jpg',
     'Spatial Sound', 'Triple Level Spatial Sound for Deeper Immersion',
     'Three levels of up-firing drivers fill the room with realistic 3D spatial audio from every direction.'),
]

# ── 스펙 (핵심 20개) ───────────────────────────────────────────────────────
SPECS = {
    'Type':                    'Soundbar with Wireless Subwoofer',
    'Channels':                '9.1.5ch (3.1.3)',
    'Total_Output_W':          '400',
    'Dolby_Atmos':             'Yes',
    'DTS_X':                   'Yes',
    'Triple_Up_Firing':        'Yes (World First)',
    'AI_Sound_Pro':            'Yes',
    'Bass_Blast_Plus':         'Yes',
    'WOW_Orchestra':           'Yes',
    'WOW_Interface':           'Yes',
    'WOW_Bracket':             'Yes (for LG OLED C Series)',
    'HDMI_eARC':               'Yes',
    'HDMI_In':                 '1',
    'Optical':                 '1',
    'Bluetooth':               '5.0',
    'Wi_Fi':                   'Yes',
    'AirPlay_2':               'Yes',
    'Chromecast':              'Yes',
    'Pass_Through_4K':         'Yes (VRR / ALLM)',
    'Dimension_Main_mm':       '975 x 63 x 125',
    'Dimension_Sub_mm':        '221 x 390 x 313',
    'Model':                   NEW_CODE,
}

# ── 유틸 ──────────────────────────────────────────────────────────────────
def jsstr(s):
    if s is None: s = ''
    s = str(s).replace('™','TM').replace('®','R').replace('’',"'")
    s = s.replace('\\','\\\\').replace('"','\\"')
    return re.sub(r'\s+',' ',s.replace('\n',' ').replace('\r','').replace('\t',' ')).strip()

def image_dims(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'Range':'bytes=0-65536','User-Agent':'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=15).read()
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
    pat = re.compile(r'(?<=[,{])\s*'+re.escape(field)+r'\s*:\s*(\[[\s\S]*?\]|\{[\s\S]*?\})',re.DOTALL)
    m=pat.search(entry)
    if not m: print(f'  WARNING: {field} not found'); return entry
    return entry[:m.start(1)]+new_val+entry[m.end(1):]

def replace_str_field(entry, field, new_val):
    pat = re.compile(r'(?<=[,{])'+re.escape(field)+r':"(?:[^"\\]|\\.)*"')
    m=pat.search(entry)
    if not m: print(f'  WARNING: str {field} not found'); return entry
    return entry[:m.start()]+f'{field}:"{new_val}"'+entry[m.end():]

# ── 치수 fetch ────────────────────────────────────────────────────────────
print('Fetching dimensions...')
all_paths = GAL_PATHS + [p for p,*_ in FEAT_LIST]
dims = {}
for p in all_paths:
    url = CDN_BASE+p
    w,h = image_dims(url)
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
print(f'\nUpdating v6_20 ({OLD_CODE} → {NEW_CODE})...')
v620=open(V6_20,encoding='utf-8').read()
idx=v620.find(f'{{id:"{OLD_CODE}"')
if idx<0: print('ERROR: entry not found'); import sys; sys.exit(1)
nxt=v620.find('{id:"',idx+10)
entry_old=v620[idx:nxt]
print(f'  Old: {len(entry_old):,} chars')
entry_new=replace_str_field(entry_old,'id',NEW_CODE)
entry_new=replace_field(entry_new,'gal',new_gal_js)
entry_new=replace_field(entry_new,'feat',new_feat_js)
entry_new=replace_field(entry_new,'sp',new_sp_js)
entry_new=replace_str_field(entry_new,'nm','LG Soundbar SC9S 9.1.5ch 400W Dolby Atmos')
entry_new=replace_str_field(entry_new,'pr','4999')
entry_new=replace_str_field(entry_new,'url','https://www.lg.com/sa_en/speakers/soundbars/sc9s/')
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
idx2=v_final.find(f'{{id:"{NEW_CODE}"'); nxt2=v_final.find('{id:"',idx2+10)
e=v_final[idx2:nxt2]
print(f'\n✅ {NEW_CODE} gal:{e[:e.find("feat:")].count("{a:\"View ")} feat:{e[e.find("feat:"):e.find(",sp:")].count("{a:\"")} size:{len(e):,}')
