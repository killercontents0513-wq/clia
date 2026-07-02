"""
RNC7 크롤 (v6_20 의 RNC7 항목 재크롤 - 불완전한 데이터 갱신)
- 제품: LG XBOOM RNC7 Party Speaker
- 갤러리: 10장 in /images/speakers/rnc7_dsauelk_emsj_sa_en_c/gallery/
- 피처: 11장 desktop 기반
- 스펙: 파티 스피커 주요 항목
- URL: https://www.lg.com/sa_en/speakers/party-speakers/rnc7/
"""
import re, sys, io, struct, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

V6_20    = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
CODE     = 'RNC7'
CDN_BASE = 'https://www.lg.com/content/dam/channel/wcms/sa_en'

TOP_ORDER = ['SC9S', 'SH5A', 'RNC5', 'RNC7', 'LSEL6333D', 'LT19HBHSIN', 'S90TR', 'S80TR', 'S45TR',
             '32GS95UV-B', 'WTV17HHD', '27US550-W', 'WK1310BST', 'RH10V9PV2W', 'WFV1214BST1']

# ── 갤러리: 10장 ────────────────────────────────────────────────────────────
GAL_BASE  = '/images/speakers/rnc7_dsauelk_emsj_sa_en_c/gallery/'
GAL_PATHS = [GAL_BASE + f'large{str(i).zfill(2)}.jpg' for i in range(1, 11)]

# ── 피처 (11장 Desktop) ──────────────────────────────────────────────────────
FEAT_BASE = '/images/av/features/'
FEAT_LIST = [
    (FEAT_BASE + 'AV-XBOOM-RNC7-01-Identity-Desktop.jpg',
     'XBOOM RNC7', 'LG XBOOM RNC7 The Ultimate Party Speaker',
     'LG XBOOM RNC7 delivers powerful 1000W sound, DJ features, karaoke, and dazzling LED lighting for unforgettable parties.'),
    (FEAT_BASE + 'AV-XBOOM-RNC7-02-SuperBass-Desktop.jpg',
     'Super Bass', 'Bass Blast+ & Super Bass Boost',
     'Experience thundering bass with dual subwoofers and Bass Blast+ technology that shakes the room.'),
    (FEAT_BASE + 'AV-XBOOM-RNC7-03-LEDLighting-Desktop.jpg',
     'LED Lighting', 'Dazzling Dual LED Lighting',
     'Dual 20W LED panels with 40+ colors and patterns sync with your music for a mesmerizing light show.'),
    (FEAT_BASE + 'AV-XBOOM-RNC7-04-DJControl-Desktop.jpg',
     'DJ Pad', 'Professional DJ Control Panel',
     'Built-in DJ pad with effects, loops, and scratch controls for advanced mixing and sound manipulation.'),
    (FEAT_BASE + 'AV-XBOOM-RNC7-05-DJApp-Desktop.jpg',
     'DJ App', 'LG XBOOM App with Remote DJ',
     'Control mixing, effects, and lighting from your smartphone with the full-featured LG XBOOM DJ app.'),
    (FEAT_BASE + 'AV-XBOOM-RNC7-06-Karaoke-Desktop.jpg',
     'Karaoke Pro', 'Professional Karaoke System',
     'Dual microphone inputs, echo control, key changer, and voice cancellation for professional karaoke.'),
    (FEAT_BASE + 'AV-XBOOM-RNC7-07-Wireless-Desktop.jpg',
     'Wireless Freedom', 'Bluetooth 5.0 Multi-Connection',
     'Connect up to 5 devices simultaneously via Bluetooth 5.0 for seamless multi-device control.'),
    (FEAT_BASE + 'AV-XBOOM-RNC7-08-Recording-Desktop.jpg',
     'USB Recording', 'Built-in Recording Function',
     'Record your performances and mixes directly to USB or microSD card with one-touch recording.'),
    (FEAT_BASE + 'AV-XBOOM-RNC7-09-Portability-Desktop.jpg',
     'Portable Design', 'Premium Black Steel Construction',
     'Heavy-duty construction with convenient handle for easy transport to any party venue.'),
    (FEAT_BASE + 'AV-XBOOM-RNC7-10-EQModes-Desktop.jpg',
     'EQ Modes', '15+ EQ Presets & Custom EQ',
     'Choose from 15+ preset equalizer modes or create your own perfect sound signature.'),
    (FEAT_BASE + 'AV-XBOOM-RNC7-11-BatteryLife-Desktop.jpg',
     'Long Battery', '12-Hour Battery Life',
     'Rechargeable 5,000mAh battery provides up to 12 hours of non-stop party power.'),
]

# ── 스펙 ──────────────────────────────────────────────────────────────────
SPECS = {
    'Type':                'XBOOM Party Speaker',
    'Speaker_System':      '2-Way 4 Speaker (2" x2 Tweeter, 6.5" Woofer x2)',
    'Total_Output_W':      '1000',
    'Bass_Blast_Plus':     'Yes (Dual Subwoofer)',
    'LED_Lighting':        'Dual 20W LED (40+ Colors & Patterns)',
    'DJ_Function':         'Yes (DJ Pad + DJ App)',
    'Karaoke':             'Yes (2 Mic Input, Key Changer, Voice Canceller)',
    'Recording':           'Yes (USB/microSD)',
    'Bluetooth':           '5.0 (Multi: up to 5 devices)',
    'AUX_Input':           '1 (3.5mm)',
    'USB_Input':           '2 (USB-A for recording)',
    'Microphone_Input':    '2 (6.3mm with Mix Control)',
    'Guitar_Input':        '1 (6.3mm)',
    'EQ_Modes':            '15+ Presets + Custom EQ',
    'Special_Effects':     'Echo / Delay / Reverb / Chorus / Flanger + more',
    'Battery_Capacity':    '5,000mAh',
    'Battery_Life_Hours':  '12',
    'Charging_Time':       '5-6 hours (DC 19V)',
    'Power_Supply':        'Rechargeable Li-ion + AC Adapter (110-240V)',
    'Dimension_mm':        '400 x 890 x 360',
    'Net_Weight_kg':       '28.5',
    'Color':               'Black Steel',
    'Model':               CODE,
}

# ── 유틸 ──────────────────────────────────────────────────────────────────
def jsstr(s):
    if s is None: s=''
    s=str(s).replace(chr(0x2122),'TM').replace(chr(0xae),'R').replace(chr(0x2019),"'")
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
entry_new=replace_str_field(entry_new,'nm','LG XBOOM RNC7 1000W Party Speaker with DJ & Karaoke')
entry_new=replace_str_field(entry_new,'pr','1299')
entry_new=replace_str_field(entry_new,'url','https://www.lg.com/sa_en/speakers/party-speakers/rnc7/')
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
print(f'\n✅ {CODE} gal:{e[:e.find("feat:")].count("{a:")} feat:{e[e.find("feat:"):e.find(",sp:")].count("{a:")} size:{len(e):,}')
