#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
import os

# READ CRAWL DATA
with open('rnc7_data.json', 'r', encoding='utf-8') as f:
    crawl_data = json.load(f)

# READ v6_20.html
with open('LG_AI_Content_Hub_v6_20.html', 'r', encoding='utf-8') as f:
    html = f.read()

# EXTRACT EXISTING RNC7 DATA
print("[Step 1] Extracting existing RNC7 metadata...")
# Find RNC7 entry up to next product or end
rnc7_start = html.find('{id:"RNC7"')
if rnc7_start == -1:
    print("[FAIL] RNC7 not found in v6_20.html")
    exit(1)

# Find the end of RNC7 entry (next {id:" or end of products array)
rnc7_temp_end = html.find('{id:"', rnc7_start + 10)
if rnc7_temp_end == -1:
    rnc7_temp_end = len(html)

existing_data = html[rnc7_start:rnc7_temp_end]

# Extract metadata
meta = {}
for key, pattern in [
    ('nm', r'nm:"([^"]+)"'),
    ('pr', r'pr:"([^"]+)"'),
    ('op', r'op:"([^"]+)"'),
    ('dv', r'dv:"([^"]+)"'),
    ('cat', r'cat:"([^"]+)"'),
    ('sub', r'sub:"([^"]+)"'),
    ('ico', r'ico:"([^"]+)"'),
]:
    m = re.search(pattern, existing_data)
    if m:
        meta[key] = m.group(1)

print(f"[OK] Name: {meta.get('nm', 'N/A')[:60]}")
print(f"[OK] Price: {meta.get('pr')} ({meta.get('op')})")

# NORMALIZE PATHS
print("[Step 2] Normalizing gallery paths...")
base_folder = "home-theaters/rnc7_dsauelk_emsj_sa_en_c"

gal_normalized = []
for i, img in enumerate(crawl_data['gal']):
    p = img['p']
    # Remove wrong prefix and add correct folder
    if p.startswith('home-theaters/gallery/'):
        p_clean = p.replace('home-theaters/gallery/', '')
    elif p.startswith('home-theaters/rnc7_dsauelk_emsj_sa_en_c/gallery/'):
        p_clean = p.replace('home-theaters/rnc7_dsauelk_emsj_sa_en_c/', '')
    else:
        p_clean = p

    # Final path format
    final_path = f"/images/{base_folder}/gallery/{p_clean.split('/')[-1]}"

    gal_normalized.append({
        'a': f"View {i+1}",
        'p': final_path,
        'w': img.get('w', 0),
        'h': img.get('h', 0)
    })

print(f"[OK] {len(gal_normalized)} gallery images normalized")
print(f"  Sample: {gal_normalized[0]['p']}")

# CLEAN FEATURE PATHS
print("[Step 3] Normalizing feature paths...")
feat_normalized = []
for feat in crawl_data['feat']:
    p = feat['p']
    if not p.startswith('/images/'):
        p = '/images/' + p
    feat_normalized.append({
        'a': feat.get('a', ''),
        'p': p,
        't': feat.get('t', ''),
        'd': feat.get('d', ''),
        'w': feat.get('w', 1600),
        'h': feat.get('h', 900)
    })

print(f"[OK] {len(feat_normalized)} features normalized")

# BUILD ENTRY STRING (JavaScript object format, not JSON)
print("[Step 4] Building v6_20 entry...")

def to_js_array(items):
    """Convert to JavaScript array format (no quotes on keys)"""
    result = []
    for item in items:
        parts = []
        for k, v in item.items():
            if isinstance(v, str):
                v_str = v.replace('"', '\\"')
                parts.append(f'{k}:"{v_str}"')
            elif isinstance(v, (int, float)):
                parts.append(f'{k}:{v}')
            elif isinstance(v, bool):
                parts.append(f'{k}:{"true" if v else "false"}')
            elif isinstance(v, list):
                parts.append(f'{k}:{json.dumps(v, separators=(",",":"), ensure_ascii=False)}')
            else:
                parts.append(f'{k}:{json.dumps(v, ensure_ascii=False)}')
        result.append('{' + ','.join(parts) + '}')
    return '[' + ','.join(result) + ']'

gal_str = to_js_array(gal_normalized)
feat_str = to_js_array(feat_normalized)
sp_str = json.dumps(crawl_data.get('sp', []), separators=(',', ':'), ensure_ascii=False)

entry = (
    '{id:"RNC7",'
    f'dv:"{meta.get("dv", "")}",'
    f'cat:"{meta.get("cat", "")}",'
    f'sub:"{meta.get("sub", "")}",'
    f'ico:"{meta.get("ico", "")}",'
    f'nm:"{meta.get("nm", "")}",'
    f'pr:"{meta.get("pr", "")}",'
    f'op:"{meta.get("op", "")}",'
    'url:"https://www.lg.com/sa_en/speakers/party-speakers/rnc7/",'
    'crawled:true,'
    f'gal:{gal_str},'
    f'feat:{feat_str},'
    f'sp:{sp_str},'
    'amz_title:"",amz_desc:"",bul:[],faq:[],promo:"",disc:"",kw:[]'
    '},'  # ADD COMMA HERE
)

print(f"[OK] Entry size: {len(entry)} chars")

# FIND AND REPLACE RNC7 IN v6_20.html
print("[Step 5] Updating v6_20.html...")
# Find RNC7 entry (from {id:" to next {id:" or end of products)
rnc7_start = html.find('{id:"RNC7"')
if rnc7_start == -1:
    print("[FAIL] RNC7 not found")
    exit(1)

# Find next entry or end
rnc7_end = html.find('{id:"', rnc7_start + 10)
if rnc7_end == -1:
    # RNC7 is the last entry - find before ]
    rnc7_end = html.find(']', rnc7_start)

# Replace
html_new = html[:rnc7_start] + entry + html[rnc7_end:]

# BACKUP AND SAVE
backup_path = 'LG_AI_Content_Hub_v6_20.pre_rnc7_integration.html'
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"[OK] Backup: {backup_path}")

with open('LG_AI_Content_Hub_v6_20.html', 'w', encoding='utf-8') as f:
    f.write(html_new)
print(f"[OK] Updated: LG_AI_Content_Hub_v6_20.html")

# VERIFY
print("[Step 6] Verification...")
verify_match = re.search(r'\{id:"RNC7"[^}]*?gal:\[(.*?)\]', html_new, re.DOTALL)
if verify_match:
    gal_count = verify_match.group(1).count('"a":')
    print(f"[OK] Verified RNC7 with {gal_count} gallery items")
else:
    print("[WARN] Could not verify RNC7")

print(f"\n=== INTEGRATION COMPLETE ===")
print(f"Product: RNC7")
print(f"Gallery: {len(gal_normalized)} items")
print(f"Features: {len(feat_normalized)} items")
print(f"Specs: {len(crawl_data.get('sp', []))} items")
print(f"\nNext: reorder_products.py")
