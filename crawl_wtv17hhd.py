"""
WTV17HHD 크롤 스크립트 (one-shot)
- LG.com PDP 신규 다운로드
- 갤러리/피처 추출 + 치수
- 스펙/가격/제품명 추출
- v6_20 엔트리 교체
- CDN prefix 자동 제거 (/content/dam/channel/wcms/sa_en → 제거)
- 순서: WTV17HHD → 27US550-W → WK1310BST → RH10V9PV2W → WFV1214BST1
"""
import re, sys, io, struct, time
import urllib.request, concurrent.futures

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

URL       = 'https://www.lg.com/sa_en/washing-machines/top-load/wtv17hhd/'
CDN_BASE  = 'https://www.lg.com/content/dam/channel/wcms/sa_en'  # CLIA CDN prefix
CODE      = 'WTV17HHD'
V6_20     = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html'
SAVE      = f'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/bulk_html/{CODE}.html'
TOP_ORDER = ['WTV17HHD', '27US550-W', 'WK1310BST', 'RH10V9PV2W', 'WFV1214BST1']

DAM_PREFIX = '/content/dam/channel/wcms/sa_en'  # 저장 시 제거할 prefix

# ── 유틸 ────────────────────────────────────────────────────────────────────
def jsstr(s):
    if s is None: s = ''
    s = str(s).replace('\u2122','TM').replace('\u00ae','R').replace('\u2019',"'")
    s = s.replace('\\','\\\\').replace('"','\\"')
    return re.sub(r'\s+',' ', s.replace('\n',' ').replace('\r','').replace('\t',' ')).strip()

def strip_prefix(p):
    """CDN prefix 제거: /content/dam/channel/wcms/sa_en/images/... → /images/..."""
    if p.startswith(DAM_PREFIX):
        return p[len(DAM_PREFIX):]
    return p

def fetch(url, retry=3):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
    }
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers=hdr)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:
            print(f'  retry {i+1}: {e}'); time.sleep(2)
    return b''

def image_dims(url):
    try:
        req = urllib.request.Request(url, headers={'Range':'bytes=0-65536','User-Agent':'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=12).read()
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
        if data[:4]==b'RIFF' and data[8:12]==b'WEBP':
            if data[12:16]==b'VP8 ':
                return struct.unpack('<H',data[26:28])[0]&0x3FFF, struct.unpack('<H',data[28:30])[0]&0x3FFF
            elif data[12:16]==b'VP8L':
                bits=struct.unpack('<I',data[21:25])[0]
                return (bits&0x3FFF)+1, ((bits>>14)&0x3FFF)+1
    except: pass
    return 0, 0

def clean(s):
    s = re.sub(r'<[^>]+>','',s)
    s = re.sub(r'&amp;','&',s); s=re.sub(r'&lt;','<',s); s=re.sub(r'&gt;','>',s)
    s = re.sub(r'&#x?[0-9a-fA-F]+;','',s)
    return re.sub(r'\s+',' ',s).strip()

def get_feat_text(html, path):
    fn   = path.split('/')[-1]
    stem = fn.rsplit('.',1)[0]
    positions = [m.start() for m in re.finditer(re.escape(stem), html, re.IGNORECASE)]
    best = next((p for p in positions if 50000 < p < len(html)-2000), None)
    if not best and positions: best = positions[0]
    if not best: return '', ''
    snip = html[max(0,best-300):best+4000]
    hl = re.search(r'c-text-contents__headline[^>]*>([\s\S]{1,400}?)</div', snip)
    bd = re.search(r'c-text-contents__body[^>]*>([\s\S]{1,1000}?)</div', snip)
    return clean(hl.group(1)) if hl else '', clean(bd.group(1)) if bd else ''

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

# ══════════════════════════════════════════════════════════════════════════
print('='*60)
print(f'CRAWLING: {CODE}  {URL}')
print('='*60)

# ── STEP 1: HTML 다운로드 ───────────────────────────────────────────────
print('\n[1] Downloading PDP...')
raw = fetch(URL)
if len(raw) < 100000:
    print(f'  ERROR: {len(raw)} bytes — too small'); sys.exit(1)
html = raw.decode('utf-8', errors='replace')
with open(SAVE,'w',encoding='utf-8') as f: f.write(html)
print(f'  OK: {len(html):,} chars → {SAVE}')

# ── STEP 2: 제품명 / 가격 ───────────────────────────────────────────────
print('\n[2] Name & Price')
nm = ''
nm_m = re.search(r'"name"\s*:\s*"((?:[^"\\]|\\.)+)"', html)
if nm_m:
    nm = nm_m.group(1).replace('\\"','"').replace('\\\\','\\')
if not nm:
    h1 = re.search(r'<h1[^>]*>([\s\S]{1,200}?)</h1>', html)
    nm = clean(h1.group(1)) if h1 else CODE
print(f'  Name: {nm}')

price = ''
pr_m = re.search(r'"price"\s*:\s*"?([\d,\.]+)"?', html)
if pr_m: price = pr_m.group(1).replace(',','')
if not price: price = '0'
print(f'  Price: SAR {price}')

# ── STEP 3: 전체 CDN 이미지 수집 ─────────────────────────────────────────
print('\n[3] Collecting images')
all_paths = list(dict.fromkeys(re.findall(
    r'/content/dam/channel/wcms/sa_en/images/[^\s"\'<>?#]+\.(?:jpg|jpeg|png|webp)',
    html, re.IGNORECASE
)))
print(f'  Total CDN images: {len(all_paths)}')

# jcr rendition 경로 제외 (thum-*, /jcr:content/ 포함)
all_paths = [p for p in all_paths if 'jcr:content' not in p and 'thum-' not in p.split('/')[-1]]
print(f'  After jcr filter: {len(all_paths)}')

# 제품 코드 기반 필터
code_lower = CODE.lower()
prod_paths = [p for p in all_paths
              if code_lower in p.lower()
              or re.search(r'/ha/', p, re.IGNORECASE)  # 세탁기 공통 카테고리
              and ('washing' in p.lower() or '/wm/' in p.lower() or 'top-load' in p.lower())]

# 좁혀지지 않으면 전체 사용
if len(prod_paths) < 3:
    prod_paths = all_paths

print(f'  Product paths: {len(prod_paths)}')
for p in prod_paths: print(f'    {strip_prefix(p)}')

# ── STEP 4: 갤러리 / 피처 분류 ─────────────────────────────────────────
print('\n[4] Classify')

def is_mobile(p):
    fn = p.split('/')[-1].lower()
    return bool(re.search(r'[-_]m\.(?:jpg|jpeg|png|webp)$', fn) or '-mobile.' in fn)

def is_gallery(p):
    fn = p.split('/')[-1].lower()
    return bool(
        'gallery' in p.lower() or
        re.search(r'(?:^|[-_])z[-_]\d+', fn) or
        re.search(r'large\d+', fn) or
        fn.endswith('-2010.jpg') or fn.endswith('-2010.jpeg') or
        re.search(r'\d+x\d+-\d+\.jpg$', fn)
    )

def is_feat(p):
    fn = p.split('/')[-1].lower()
    return bool(
        'feature' in p.lower() or
        re.search(r'feat', fn) or
        re.search(r'[-_][df]\.(?:jpg|jpeg|png|webp)$', fn)
    )

def is_desktop(p):
    fn = p.split('/')[-1].lower()
    return not bool(re.search(r'[-_]m\.(?:jpg|jpeg|png|webp)$', fn) or '-mobile.' in fn)

# 갤러리: 파일명 기준 필터 (jcr/thum 이미 제외됨)
gal_all  = [p for p in prod_paths if is_gallery(p) and not is_mobile(p)]

# 갤러리 최고해상도 선택: 파일명 그룹별 최대 크기
# -2010 우선, 아니면 large/Z- 순
gal_main = [p for p in gal_all if '-2010.' in p.split('/')[-1]]
if not gal_main:
    gal_main = [p for p in gal_all if re.search(r'large\d+', p.split('/')[-1].lower())]
if not gal_main:
    gal_main = [p for p in gal_all if re.search(r'z-\d+', p.split('/')[-1].lower())]
if not gal_main:
    gal_main = gal_all

# 피처: 데스크톱만
feat_all  = [p for p in prod_paths if not is_gallery(p) and not is_mobile(p)]
feat_desk = [p for p in feat_all if is_desktop(p)]
if not feat_desk:
    feat_desk = feat_all

print(f'  Gallery: {len(gal_main)}')
for p in gal_main: print(f'    {strip_prefix(p)}')
print(f'  Feature: {len(feat_desk)}')
for p in feat_desk: print(f'    {strip_prefix(p)}')

# ── STEP 5: 이미지 치수 병렬 fetch ────────────────────────────────────
print('\n[5] Fetching dimensions')
selected = gal_main + feat_desk
urls = [CDN_BASE + p for p in selected]

dims = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    futs = {ex.submit(image_dims, u): u for u in urls}
    for f in concurrent.futures.as_completed(futs):
        u = futs[f]; w,h = f.result(); dims[u] = (w,h)
        print(f'  {u.split("/")[-1]}: {w}x{h}')

# ── STEP 6: 피처 텍스트 ─────────────────────────────────────────────
print('\n[6] Feature texts')
feat_items = []
for path in feat_desk:
    url = CDN_BASE + path
    w,h = dims.get(url,(0,0))
    t,d = get_feat_text(html, path)
    fn = path.split('/')[-1].rsplit('.',1)[0]
    label = t if t else re.sub(r'[-_]+',' ', re.sub(r'^.*?(?:feature[-_]|feat[-_]|\d{2}[-_])',' ',fn,1)).strip().title()
    feat_items.append({'p':strip_prefix(path),'a':label,'t':t,'d':d,'w':w,'h':h})
    print(f'  [{len(feat_items)}] {fn[-45:]}: {label[:50]} ({w}x{h})')

# ── STEP 7: 스펙 추출 ───────────────────────────────────────────────
print('\n[7] Specs')
specs = {}

# Method 1: c-compare-selling
pairs = re.findall(
    r'c-compare-selling__spec-name[^>]*>([\s\S]{1,200}?)</(?:p|div|span)>[\s\S]{0,400}?'
    r'c-compare-selling__spec-desc[^>]*>([\s\S]{1,400}?)</(?:p|div|span)>',
    html)
print(f'  c-compare-selling: {len(pairs)}')
for sn,sd in pairs:
    k = re.sub(r'\s+','_',clean(sn))
    v = clean(sd)
    if k and v: specs[k] = v; print(f'    {k}: {v[:70]}')

# Method 2: Key Features 목록
kf_m = re.search(r'id="keyFeatureList"[^>]*>([\s\S]{0,3000}?)</ul>', html)
if kf_m:
    kf_items = re.findall(r'<(?:li|span)[^>]*>([\s\S]{1,200}?)</(?:li|span)>', kf_m.group(1))
    kf_clean = [clean(x) for x in kf_items if clean(x)]
    print(f'  Key Features: {kf_clean}')
    for i,feat in enumerate(kf_clean):
        k = f'Feature_{i+1}'
        if feat and k not in specs: specs[k] = feat

print(f'  Total specs: {len(specs)}')

# ── STEP 8: JS 빌드 ─────────────────────────────────────────────────
print('\n[8] Building JS')

gal_parts = []
for i,path in enumerate(gal_main,1):
    url = CDN_BASE + path
    w,h = dims.get(url,(0,0))
    sp  = strip_prefix(path)
    gal_parts.append(f'{{a:"View {i}",p:"{sp}",w:{w},h:{h}}}')
new_gal_js = '['+','.join(gal_parts)+']'
print(f'  gal: {len(gal_parts)}')

feat_parts = []
for item in feat_items:
    feat_parts.append(
        f'{{a:"{jsstr(item["a"])}",p:"{item["p"]}",t:"{jsstr(item["t"])}",d:"{jsstr(item["d"])}",w:{item["w"]},h:{item["h"]}}}')
new_feat_js = '['+','.join(feat_parts)+']'
print(f'  feat: {len(feat_parts)}')

sp_parts = [f'"{k}":"{jsstr(v)}"' for k,v in specs.items()]
new_sp_js = '{'+','.join(sp_parts)+'}'
print(f'  sp: {len(sp_parts)}')

# ── STEP 9: v6_20 엔트리 교체 ────────────────────────────────────────
print('\n[9] Updating v6_20')
v620 = open(V6_20, encoding='utf-8').read()
idx  = v620.find(f'{{id:"{CODE}"')
if idx < 0:
    print(f'  ERROR: {CODE} not found in v6_20'); sys.exit(1)
nxt  = v620.find('{id:"', idx+10)
entry_old = v620[idx:nxt]
print(f'  Old: {len(entry_old):,} chars')

entry_new = replace_field(entry_old, 'gal', new_gal_js)
entry_new = replace_field(entry_new, 'feat', new_feat_js)
entry_new = replace_field(entry_new, 'sp', new_sp_js)
entry_new = replace_str_field(entry_new, 'nm', jsstr(nm))
entry_new = replace_str_field(entry_new, 'pr', price)
entry_new = replace_str_field(entry_new, 'crawled', 'true')

print(f'  New: {len(entry_new):,} chars')
v620_new = v620[:idx] + entry_new + v620[nxt:]
open(V6_20,'w',encoding='utf-8').write(v620_new)
print('  Saved.')

# ── STEP 10: 순서 재배치 ─────────────────────────────────────────────
print('\n[10] Reordering')
html2   = open(V6_20, encoding='utf-8').read()
fi      = html2.find('{id:"')
ao      = html2.rfind('[', 0, fi)
ac      = html2.find('];', fi)
before  = html2[:ao+1]; after = html2[ac:]; body = html2[ao+1:ac]

splits  = list(re.finditer(r'(?=\{id:")', body))
entries = []
for i,m in enumerate(splits):
    s = m.start(); e = splits[i+1].start() if i+1<len(splits) else len(body)
    raw = body[s:e].rstrip(',\n ')
    cm  = re.match(r'\{id:"([^"]+)"', raw)
    entries.append((cm.group(1) if cm else f'UNK_{i}', raw))

top_set  = set(TOP_ORDER)
code_map = {c:e for c,e in entries}
new_entries = [(c,code_map[c]) for c in TOP_ORDER if c in code_map] + \
              [(c,e) for c,e in entries if c not in top_set]
open(V6_20,'w',encoding='utf-8').write(before+'\n'+',\n'.join(e for _,e in new_entries)+'\n'+after)

print(f'  Top 5: {[c for c,_ in new_entries[:5]]}')
print(f'  Total: {len(new_entries)}')

# ── 최종 요약 ────────────────────────────────────────────────────────
print(f'\n{"="*60}')
print(f'✅ {CODE} 크롤 완료!')
print(f'   nm   : {nm}')
print(f'   pr   : SAR {price}')
print(f'   gal  : {len(gal_parts)}장')
print(f'   feat : {len(feat_parts)}장')
print(f'   sp   : {len(sp_parts)}개')
print(f'{"="*60}')
