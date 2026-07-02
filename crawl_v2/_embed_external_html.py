# -*- coding: utf-8 -*-
# Embed external HTML files (Content Guide + A+ Builder) into v6_18.html as base64 constants
# so the file is fully self-contained for moving to another computer.
import base64, os, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
HTML = f'{BASE}/LG_AI_Content_Hub_v6_18.html'

FILES = {
    'EMBED_GUIDE_B64':   f'{BASE}/global-content-image-guide.html',
    'EMBED_APLUS_B64':   f'{BASE}/amazon-aplus/index.html',
}

# Load each and base64-encode
b64s = {}
for var, path in FILES.items():
    if not os.path.exists(path):
        print(f'[WARN] missing {path}'); continue
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    b64s[var] = b64
    print(f'  {var}: {os.path.getsize(path):,} bytes → {len(b64):,} b64 chars')

# Read v6_18
with open(HTML, encoding='utf-8') as f:
    html = f.read()

# Backup
bk = HTML.replace('.html', '.pre_embed_html.html')
with open(bk, 'w', encoding='utf-8') as f: f.write(html)
print(f'backup: {bk}')

# 1) Inject the JS constants + helpers right after the <script> tag (find first <script> in body)
# We'll insert before the CDN constant line: `const CDN='...'`
inject_marker = "const CDN='https://www.lg.com/content/dam/channel/wcms/sa_en';"
if inject_marker not in html:
    print('[ERR] CDN marker not found — aborting'); sys.exit(1)

helper_js = (
    '// ===== Embedded external HTML files (for fully self-contained portable HTML) =====\n'
    f'const EMBED_GUIDE_B64="{b64s.get("EMBED_GUIDE_B64","")}";\n'
    f'const EMBED_APLUS_B64="{b64s.get("EMBED_APLUS_B64","")}";\n'
    'function _embedBlobUrl(b64){if(!b64)return "about:blank";try{const bin=atob(b64);const arr=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)arr[i]=bin.charCodeAt(i);return URL.createObjectURL(new Blob([arr],{type:"text/html;charset=utf-8"}));}catch(e){console.error("embed decode failed",e);return "about:blank";}}\n'
    'function openContentGuide(){window.open(_embedBlobUrl(EMBED_GUIDE_B64),"_blank");}\n'
    'function getAplusBuilderUrl(){return _embedBlobUrl(EMBED_APLUS_B64);}\n'
)

# Insert BEFORE the CDN marker
html2 = html.replace(inject_marker, helper_js + inject_marker)

# 2) Replace the 3 occurrences of window.open for content guide
old_guide = "window.open('./global-content-image-guide.html','_blank')"
new_guide = "openContentGuide()"
n_guide = html2.count(old_guide)
html2 = html2.replace(old_guide, new_guide)
print(f'  window.open guide: {n_guide} replaced')

# 3) Replace the iframe src for a+ builder
old_ifr_check = "ifr.src.includes('amazon-aplus')"
# The full line: `if(ifr&&!ifr.src.includes('amazon-aplus'))ifr.src='amazon-aplus/index.html';`
# We want the check to be "not already a blob URL" and to set via helper. Simplest: replace the src literal.
old_ifr_src = "ifr.src='amazon-aplus/index.html'"
new_ifr_src = "ifr.src=getAplusBuilderUrl()"
n_ifr = html2.count(old_ifr_src)
html2 = html2.replace(old_ifr_src, new_ifr_src)
# Also relax the guard condition — it checks for 'amazon-aplus' in src, but after our change src becomes a blob: URL, so the check would re-assign every time. Change to a plain "not set" check.
old_guard = "if(ifr&&!ifr.src.includes('amazon-aplus'))"
new_guard = "if(ifr&&!ifr.src.startsWith('blob:'))"
n_guard = html2.count(old_guard)
html2 = html2.replace(old_guard, new_guard)
print(f'  iframe src: {n_ifr} src / {n_guard} guard replaced')

# 4) Verify no leftover local refs
leftovers = re.findall(r'["\'](\.?/?(amazon-aplus/index\.html|global-content-image-guide\.html))["\']', html2)
if leftovers:
    print(f'[WARN] leftover refs: {set(leftovers)}')
else:
    print('[OK] no external HTML refs remain')

# Stats
print(f'\nsize: {len(html):,} → {len(html2):,} ({len(html2)-len(html):+,} chars)')

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html2)
print(f'wrote: {HTML}')
