"""Extract RH81T2SP7RM from Apr 20 backup and restore it in current HTML."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'

# Apr 20 backup (last one of the day)
with open(f'{BASE}/LG_AI_Content_Hub_v6_18.pre_A9K-SOLO.html','r',encoding='utf-8',errors='replace') as f:
    apr20 = f.read()

# Current HTML
with open(f'{BASE}/LG_AI_Content_Hub_v6_18.html','r',encoding='utf-8',errors='replace') as f:
    current = f.read()

def extract_product_entry(html, code):
    """Extract a single product JS object from P=[...] array."""
    # Find start: {id:"CODE" or {id:'CODE'
    pat = f'id:"{code}"'
    idx = html.find(pat)
    if idx < 0:
        pat = f"id:'{code}'"
        idx = html.find(pat)
    if idx < 0:
        return None, -1, -1
    # Walk back to find the opening {
    start = html.rfind('{', 0, idx)
    # Walk forward to find the matching closing } — count braces
    depth = 0
    i = start
    while i < len(html):
        c = html[i]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return html[start:i+1], start, i+1
        i += 1
    return None, -1, -1

# Extract from Apr 20
old_entry, _, _ = extract_product_entry(apr20, 'RH81T2SP7RM')
if not old_entry:
    print('ERROR: RH81T2SP7RM not found in Apr 20 backup!')
    sys.exit(1)

print(f'Apr 20 entry length: {len(old_entry):,} chars')
# Show key parts
gal_m = re.search(r'gal:\[([^\]]*)\]', old_entry)
feat_m = re.search(r'feat:\[', old_entry)
if gal_m:
    gal_count = old_entry[old_entry.find('gal:['):].count('"p":')
    # Count items in gal array
    gal_section = re.search(r'gal:\[(.*?)\],\s*feat:', old_entry, re.DOTALL)
    if gal_section:
        n_gal = gal_section.group(1).count('"p":')
        print(f'Gallery items: {n_gal}')
feat_section = re.search(r'feat:\[(.*?)\],\s*sp:', old_entry, re.DOTALL)
if feat_section:
    n_feat = feat_section.group(1).count('"p":')
    print(f'Feature items: {n_feat}')

# Extract from current
cur_entry, cur_start, cur_end = extract_product_entry(current, 'RH81T2SP7RM')
if not cur_entry:
    print('ERROR: RH81T2SP7RM not found in current HTML!')
    sys.exit(1)
print(f'Current entry length: {len(cur_entry):,} chars')

# Replace
new_html = current[:cur_start] + old_entry + current[cur_end:]

with open(f'{BASE}/LG_AI_Content_Hub_v6_18.html','w',encoding='utf-8') as f:
    f.write(new_html)

print(f'\nRestored! HTML size: {len(current):,} -> {len(new_html):,}')
print('RH81T2SP7RM restored from Apr 20 backup.')

# Show the restored entry preview
print('\n--- Apr 20 entry preview ---')
print(old_entry[:800])
print('...')
