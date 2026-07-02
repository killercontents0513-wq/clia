"""WK1310BST 전체 재크롤 + v6_20 통합"""
import re, json, os, sys, io, urllib.request, concurrent.futures as cf
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE    = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
URL     = 'https://www.lg.com/sa_en/washing-machines/washtower/wk1310bst/'
CODE    = 'WK1310BST'
CAT     = 'Washer'
SUB     = 'WashTower'
ICO     = '🏢'
DV      = 'HA'
PREFIX  = '/content/dam/channel/wcms/sa_en'
UA      = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
HTML_OUT = f'{BASE}/bulk_html/{CODE}.html'
V6_20   = f'{BASE}/LG_AI_Content_Hub_v6_20.html'

EXCLUDE = ['/gnb/','/home-page/','/banners-20','/ai-core-tech','/2025-webos/',
           '/common-icon/','/elements/icons-line/','/members-offer','/multishop',
           '/ministry-of/','/oled-speaker/','/spring-sale','/next-day',
           '/watch-it-promo','/av-wm-pto','/bundles-jan','/buy-one-get',
           '/alrajhi','/gnb-banner','/common/common-icon']

def clean(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    s = (s.replace('&#x27;',"'").replace('&amp;','&').replace('&quot;','"')
          .replace('&nbsp;',' ').replace('\u2122','™').replace('\u00ae','®')
          .replace('\u201c','"').replace('\u201d','"')
          .replace('\u2018',"'").replace('\u2019',"'")
          .replace('\\r','').replace('\\n',' ').replace('\\t',' '))
    return re.sub(r'\s+',' ',s).strip()

def jsstr(s):
    if s is None: s=''
    s=str(s)
    s=(s.replace('\u201c','"').replace('\u201d','"')
        .replace('\u2018',"'").replace('\u2019',"'")
        .replace('\u2122','™').replace('\u00ae','®'))
    s=s.replace('\\','\\\\').replace('"','\\"')
    s=s.replace('\n',' ').replace('\r','').replace('\t',' ')
    return re.sub(r'\s+',' ',s).strip()

# ── 1. FRESH DOWNLOAD ──────────────────────────────────────
print(f'▶ Fetching {URL} ...')
req = urllib.request.Request(URL, headers={'User-Agent': UA})
with urllib.request.urlopen(req, timeout=40) as r:
    raw = r.read()
with open(HTML_OUT, 'wb') as f:
    f.write(raw)
html = raw.decode('utf-8', errors='replace')
print(f'  {len(html):,} chars downloaded')

# ── 2. JSON-LD 메타 ────────────────────────────────────────
name, price, msrp = CODE, '', ''
for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL):
    try:
        d = json.loads(m.group(1))
        if isinstance(d,dict) and d.get('@type','').lower()=='product':
            name  = d.get('name') or name
            off   = d.get('offers') or {}
            if isinstance(off,dict):
                price = str(off.get('price') or '')
                psp   = off.get('priceSpecification') or {}
                if isinstance(psp,dict): msrp = str(psp.get('price') or '')
    except: pass
print(f'  Name : {name}')
print(f'  Price: {price}  MSRP: {msrp}')

# ── 3. CDN 이미지 전수 추출 ────────────────────────────────
def excl(p):
    pl=p.lower()
    return any(x in pl for x in EXCLUDE)

all_imgs = sorted(set(re.findall(
    r'/content/dam/channel/wcms/sa_en/[^"\'\ )]+?\.(?:jpg|jpeg|png|webp|gif)', html)))
all_imgs = [i for i in all_imgs
            if '/renditions/' not in i and '/jcr:content/' not in i and not excl(i)]

from collections import Counter
folder_cnt = Counter()
for i in all_imgs:
    parts = i.rstrip('/').split('/')
    if len(parts)>=4: folder_cnt['/'.join(parts[:-1])] += 1

code_l  = CODE.lower()
code_l2 = code_l.replace('-','')
product_folders = set()
for folder,n in folder_cnt.items():
    fl=folder.lower()
    if code_l in fl or code_l2 in fl:
        product_folders.add(folder)
    elif n>=6 and any(seg in fl for seg in [
        '/features/','/gallery/','/wm/','/ha/','/washing-machines/',
        '/dryers/','/dishwashers/','/vacuum','/speakers/','/washtower/']):
        product_folders.add(folder)
for i in all_imgs:
    if code_l in i.lower() or code_l2 in i.lower():
        parts=i.rstrip('/').split('/')
        if len(parts)>=4: product_folders.add('/'.join(parts[:-1]))

imgs = [i for i in all_imgs if '/'.join(i.rstrip('/').split('/')[:-1]) in product_folders]
seen=set(); imgs_dedup=[]
for i in imgs:
    fn=i.split('/')[-1].lower()
    if fn not in seen: seen.add(fn); imgs_dedup.append(i)

print(f'\n  Total product images: {len(imgs_dedup)}')
print('  Folders:')
for pf in sorted(product_folders):
    print(f'    {pf}  ({folder_cnt[pf]})')

# ── 4. 갤러리 vs 피처 분류 ────────────────────────────────
def is_feat(p):
    pl=p.lower(); return 'feature' in pl or '/features/' in pl
def is_gal(p):
    pl=p.lower(); nm=p.split('/')[-1].lower()
    if is_feat(p): return False
    if '/gallery/' in pl or '-gallery-' in pl: return True
    if re.match(r'^(d|dz|mz|s|z|l)[-_]?\d+\.', nm): return True
    if re.match(r'^\d{3,4}x\d{3,4}[-_]', nm): return True   # 1600x1062-11.jpg
    if re.match(r'^\d{3}[\._]', nm): return True
    if 'basic' in nm or 'thumbnail' in nm or 'large' in nm: return True
    return False
def is_desktop(p):
    return bool(re.search(r'(?:[-_]d(?:[-_]\d+)?\.|/desktop/|[-_]desktop[-._]|-D\.)', p.lower()))
def is_mobile(p):
    return bool(re.search(r'[-_]m(?:obile)?(?:[-_]\d+)?\.|/mobile/|[-_]mobile[-.]', p.lower()))

gallery_raw  = [i for i in imgs_dedup if is_gal(i)]
features_raw = [i for i in imgs_dedup if is_feat(i)]
desk = [i for i in features_raw if is_desktop(i)]
features_final = desk if len(desk)>=3 else [i for i in features_raw if not is_mobile(i)] or features_raw

def gal_rank(p):
    nm=p.split('/')[-1].lower()
    if 'large14' in nm or 'basic-large' in nm: return 0
    if 'large' in nm:
        m=re.search(r'large[-_]?(\d+)',nm)
        return int(m.group(1)) if m else 5
    if re.match(r'^\d{3,4}x\d{3,4}[-_](\d+)',nm):
        m=re.match(r'^\d{3,4}x\d{3,4}[-_](\d+)',nm)
        return int(m.group(1)) if m else 5
    if re.match(r'^dz[-_]',nm): return 3
    if re.match(r'^(d|z)[-_]?\d+',nm):
        m2=re.search(r'(\d+)',nm); return int(m2.group(1)) if m2 else 5
    if '450' in nm or 'basic' in nm: return 6
    return 7

gallery_final = sorted(gallery_raw, key=gal_rank)

print(f'\n  Gallery  : {len(gallery_final)}')
for g in gallery_final: print(f'    {g.split("/")[-1]}')
print(f'\n  Features : {len(features_final)}')
for f in features_final: print(f'    {f.split("/")[-1]}')

# 피처가 없으면 /wm/ 폴더 추가 탐색
wm_imgs = sorted(set(re.findall(
    r'/content/dam/channel/wcms/sa_en/images/wm/[^"\'\ )]+?\.(?:jpg|jpeg|png|webp|gif)', html)))
wm_imgs = [i for i in wm_imgs if '/renditions/' not in i and not excl(i)
           and is_desktop(i) and 'Blank' not in i]
if not features_final and wm_imgs:
    print(f'\n  /wm/ desktop fallback: {len(wm_imgs)}')
    for i in wm_imgs: print(f'    {i.split("/")[-1]}')
    features_final = wm_imgs

# ── 5. Dimensions ─────────────────────────────────────────
def image_dims(path):
    try:
        url='https://www.lg.com'+path
        req=urllib.request.Request(url,headers={'User-Agent':UA,'Range':'bytes=0-65536'})
        with urllib.request.urlopen(req,timeout=10) as r: data=r.read()
        if data[:2]==b'\xff\xd8':
            i=2
            while i<len(data)-8:
                if data[i]!=0xFF: break
                mk=data[i+1]
                if 0xC0<=mk<=0xCF and mk not in(0xC4,0xC8,0xCC):
                    return (data[i+7]<<8)|data[i+8],(data[i+5]<<8)|data[i+6]
                i+=2+((data[i+2]<<8)|data[i+3])
        if data[:8]==b'\x89PNG\r\n\x1a\n':
            return int.from_bytes(data[16:20],'big'),int.from_bytes(data[20:24],'big')
        if data[:4]==b'RIFF' and data[8:12]==b'WEBP':
            if b'VP8 ' in data[:40]:
                i2=data.index(b'VP8 ')
                return int.from_bytes(data[i2+14:i2+16],'little')&0x3FFF,int.from_bytes(data[i2+16:i2+18],'little')&0x3FFF
    except: pass
    return 0,0

all_paths = [(p,'gal') for p in gallery_final]+[(p,'feat') for p in features_final]
dim_map={}
print(f'\n  Fetching dimensions for {len(all_paths)} images...')
def get_dim(t):
    p,k=t
    if p.lower().endswith('.gif'): return p,1600,900
    w,h=image_dims(p); return p,w,h
with cf.ThreadPoolExecutor(max_workers=20) as ex:
    for p,w,h in ex.map(get_dim,all_paths):
        dim_map[p]=(w,h)
        print(f'    {"G" if (p,"gal") in all_paths else "F"} {w:>5}x{h:<5}  {p.split("/")[-1]}')

# ── 6. 피처 텍스트 ────────────────────────────────────────
def get_feat_text(fn):
    stem=fn.rsplit('.',1)[0]
    all_pos=[m.start() for m in re.finditer(re.escape(stem),html)]
    best=next((p for p in all_pos if 150000<p<700000),None)
    if best is None and all_pos: best=all_pos[0]
    if best is None: return '','',''
    snip=html[best:best+3500]
    alt_m=re.search(r'alt="([^"]{5,120})"',snip)
    hl_m =re.search(r'c-text-contents__headline[^>]*>([\s\S]{1,400}?)</div>',snip)
    bd_m =re.search(r'c-text-contents__body[^>]*>([\s\S]{1,600}?)</div>',snip)
    return (clean(alt_m.group(1)) if alt_m else '',
            clean(hl_m.group(1))  if hl_m else '',
            clean(bd_m.group(1))  if bd_m else '')

print('\n  Feature texts:')
feat_data=[]
for fp in features_final:
    fn=fp.split('/')[-1]
    alt,title,desc=get_feat_text(fn)
    feat_data.append((fp,alt,title,desc))
    print(f'    [{fn[:48]}]')
    print(f'      T: {title[:70]}')
    print(f'      D: {desc[:80]}')

# ── 7. 스펙 ───────────────────────────────────────────────
pairs=re.findall(
    r'c-compare-selling__spec-name"><p>([\s\S]*?)</p></div>'
    r'<div class="cmp-text c-compare-selling__spec-desc"><p>([\s\S]*?)</p>',html)
specs={}
for k,v in pairs:
    k=clean(k).rstrip(':').strip(); v=clean(v)
    if k and v and k not in specs: specs[k[:50]]=v[:200]
    if len(specs)>=40: break
print(f'\n  Specs: {len(specs)}')
for k,v in specs.items(): print(f'    {k}: {v}')

# ── 8. 갤러리 label ───────────────────────────────────────
def gal_label(g):
    nm=g.split('/')[-1].lower()
    if 'basic-large' in nm or 'basic_large' in nm: return 'Basic Large'
    if 'basic' in nm: return 'Basic'
    m=re.match(r'^dz[-_]?(\d+)',nm)
    if m: return f'Zoom {int(m.group(1))}'
    m=re.match(r'^\d{3,4}x\d{3,4}[-_](\d+)',nm)
    if m: return f'View {int(m.group(1))}'
    m=re.match(r'^large[-_]?(\d+)',nm)
    if m: return f'View {int(m.group(1))}'
    m=re.match(r'^(d|s|mz|z|l)[-_]?(\d+)',nm)
    if m: return f'View {int(m.group(2))}'
    m=re.search(r'(\d+)',nm)
    return f'View {int(m.group(1))}' if m else 'Detail'

def rel(p): return p[len(PREFIX):] if p.startswith(PREFIX) else p

# ── 9. JS 생성 ────────────────────────────────────────────
def fmt_price(v):
    try:
        f=float(v)
        return f'SAR {int(f):,}' if f==int(f) else f'SAR {f:,.2f}'
    except: return f'SAR {v}' if v else ''

price_fmt=fmt_price(price)

gallery_out=[{'a':gal_label(g),'p':rel(g),'w':dim_map.get(g,(0,0))[0],'h':dim_map.get(g,(0,0))[1]}
             for g in gallery_final]

features_out=[]
for fp,alt,title,desc in feat_data:
    fn=fp.split('/')[-1]; base=fn.rsplit('.',1)[0]
    kw_m=re.search(r'(?:VCM|WT)[-_]\d+[-_]?\d*[-_]?([\w\-]+?)(?:[-_]D(?:\.|\b)|$)',base,re.I)
    label=(kw_m.group(1).replace('-',' ').replace('_',' ').title() if kw_m
           else alt[:30] if alt else base[:20])
    if not title or len(title)<5: title=alt or label
    if not desc  or len(desc)<10:  desc=title
    w,h=dim_map.get(fp,(0,0))
    features_out.append({'a':label,'p':rel(fp),'t':title,'d':desc,'w':w,'h':h})

def js_gal(items):
    return '['+','.join(f'{{a:"{jsstr(g["a"])}",p:"{jsstr(g["p"])}",w:{g["w"]},h:{g["h"]}}}'
                        for g in items)+']'
def js_feat(items):
    parts=[]
    for f in items:
        wh=f',w:{f["w"]},h:{f["h"]}' if f.get('w') and f.get('h') else ''
        parts.append(f'{{a:"{jsstr(f["a"])}",p:"{jsstr(f["p"])}",t:"{jsstr(f["t"])}",d:"{jsstr(f["d"])}"{wh}}}')
    return '['+','.join(parts)+']'
def js_sp(sp):
    parts=[]
    for k,v in sp.items():
        key=re.sub(r'[^A-Za-z0-9]','_',k).strip('_')[:30]
        if not key or key[0].isdigit(): key='K_'+key
        parts.append(f'"{key}":"{jsstr(v)}"')
    return '{'+','.join(parts)+'}'

gal_js  = js_gal(gallery_out)
feat_js = js_feat(features_out)
sp_js   = js_sp(specs)

# ── 10. v6_20 갱신 ────────────────────────────────────────
with open(V6_20,'r',encoding='utf-8') as f: v620=f.read()

entry_start=v620.find(f'{{id:"{CODE}"')
if entry_start<0: print('ERROR: entry not found'); exit(1)
entry_end=v620.find('{id:"',entry_start+10)
entry_old=v620[entry_start:entry_end]
print(f'\nOld entry: {len(entry_old):,} chars')

def replace_field(entry,field,new_val):
    pat=re.compile(r'(?<=[,{])\s*'+re.escape(field)+r'\s*:\s*(\[[\s\S]*?\]|\{[\s\S]*?\})',re.DOTALL)
    m=pat.search(entry)
    if not m: print(f'  WARNING: {field} not found'); return entry
    return entry[:m.start(1)]+new_val+entry[m.end(1):]
def replace_str(entry,field,new_val):
    pat=re.compile(r'(?<=[,{])('+re.escape(field)+r':")([^"]*?)(")')
    m=pat.search(entry)
    if not m: print(f'  WARNING: str {field} not found'); return entry
    return entry[:m.start(2)]+jsstr(new_val)+entry[m.end(2):]

entry_new=entry_old
entry_new=replace_field(entry_new,'gal', gal_js)
entry_new=replace_field(entry_new,'feat',feat_js)
entry_new=replace_field(entry_new,'sp',  sp_js)
entry_new=replace_str(entry_new,'pr',price_fmt)

import shutil
if not os.path.exists(f'{BASE}/LG_AI_Content_Hub_v6_20.backup.html'):
    shutil.copy(V6_20,f'{BASE}/LG_AI_Content_Hub_v6_20.backup.html')

v620_new=v620[:entry_start]+entry_new+v620[entry_end:]
with open(V6_20,'w',encoding='utf-8') as f: f.write(v620_new)
print(f'New entry: {len(entry_new):,} chars')

# ── 11. 리스트 순서 재배치 ─────────────────────────────────
TOP_ORDER=['WK1310BST','RH10V9PV2W','WFV1214BST1']
v620=open(V6_20,encoding='utf-8').read()
first_id=v620.find('{id:"')
arr_open=v620.rfind('[',0,first_id)
arr_close=v620.find('];',first_id)
before=v620[:arr_open+1]; after=v620[arr_close:]
arr_body=v620[arr_open+1:arr_close]
splits=list(re.finditer(r'(?=\{id:")',arr_body))
entries=[]
for i,m in enumerate(splits):
    s=m.start(); e2=splits[i+1].start() if i+1<len(splits) else len(arr_body)
    raw=arr_body[s:e2].rstrip(',\n ')
    cm=re.match(r'\{id:"([^"]+)"',raw)
    entries.append((cm.group(1) if cm else f'UNK_{i}',raw))
top_codes=set(TOP_ORDER)
code_map={c:e for c,e in entries}
top_e =[( c,code_map[c]) for c in TOP_ORDER if c in code_map]
rest_e=[(c,e) for c,e in entries if c not in top_codes]
new_body=',\n'.join(e for _,e in top_e+rest_e)
open(V6_20,'w',encoding='utf-8').write(before+'\n'+new_body+'\n'+after)
print(f'\n✅ Done!')
print(f'   Gallery  : {len(gallery_out)} images')
print(f'   Features : {len(features_out)} images')
print(f'   Specs    : {len(specs)} items')
print(f'   Price    : {price_fmt}')
print(f'   Order    : {[c for c,_ in (top_e+rest_e)[:4]]}')
