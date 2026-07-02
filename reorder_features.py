"""Re-sort each product's feat[] by the section number embedded in filename
(= LG.com PDP display order). Processes ALL crawled products in v6_18.html.

Sort key: (section_major, section_minor, desktop_variant, original_pos)
- section numbers: 01, 02, 03, ..., from filename patterns
- desktop variant sorts before mobile when same section
- summary/saso/award go to the END (after all regular sections)
"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HTML = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_18.html'

def section_key(p, pos):
    """Return sort key from feature path. Lower = earlier in PDP."""
    nm = p.split('/')[-1].lower().rsplit('.',1)[0]

    # Category: summary/award goes LAST
    if any(x in nm for x in ['saso','summary','award-','-award']):
        return (99, 99, 9, pos)

    # Identify desktop (0), mobile (1), other (2) variant
    if 'desktop' in nm or re.search(r'[-_]d(?:[-_]\w+)?$', nm):
        variant = 0
    elif 'mobile' in nm or re.search(r'[-_]m(?:[-_]\w+)?$', nm):
        variant = 1
    else:
        variant = 2

    # Patterns to extract section (major, minor)
    patterns = [
        # Explicit "feature-NN[-M]" in filename (monitors, TVs)
        r'feature[-_](?:desktop[-_]|mobile[-_])?(\d{1,2})(?:[-_](\d+))?',
        # "feature-desktop-NN" (soundbars etc.)
        r'feature[-_](?:d(?:esktop)?|m(?:obile)?)[-_](\d{1,2})(?:[-_](\d+))?',
        # Model-prefix-NN[-M]-topic (washing machines)
        r'[-_](\d{1,2})(?:[-_](\d{1,2}))?[-_][a-z](?!\d)',
    ]
    major = None; minor = 0
    for pat in patterns:
        m = re.search(pat, nm)
        if m:
            major = int(m.group(1))
            minor = int(m.group(2)) if m.group(2) else 0
            break
    if major is None:
        # Fallback: trailing number
        m = re.search(r'(\d{1,2})(?!\d)', nm)
        if m: major = int(m.group(1))
        else: major = 50
    return (major, minor, variant, pos)

with open(HTML,'r',encoding='utf-8') as f:
    html = f.read()

# Find all feat:[ ... ] arrays inside the const P array.
# Walk product blocks: find `{id:"...",...` through matching `}`.
product_pat = re.compile(r'\{id:"([A-Z0-9\-]+)"')
updates = []
result = []
cursor = 0
while True:
    m = product_pat.search(html, cursor)
    if not m: break
    code = m.group(1)
    block_start = m.start()
    # Balance braces
    depth = 0; i = block_start; in_str = None
    while i < len(html):
        c = html[i]
        if in_str:
            if c == '\\': i += 2; continue
            if c == in_str: in_str = None
        else:
            if c in ('"',"'"): in_str = c
            elif c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    block_end = i+1
                    break
        i += 1
    block = html[block_start:block_end]

    # Find feat:[ ... ] inside block
    fm = re.search(r'\bfeat:\[', block)
    if not fm:
        cursor = block_end
        continue
    fs = fm.end() - 1  # position of [
    # Balance brackets
    depth = 0; j = fs; in_str = None
    while j < len(block):
        c = block[j]
        if in_str:
            if c == '\\': j += 2; continue
            if c == in_str: in_str = None
        else:
            if c in ('"',"'"): in_str = c
            elif c == '[': depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    fe = j+1
                    break
        j += 1
    feat_arr_str = block[fs:fe]  # includes outer [ ]

    # Split items. Each item is {a:"...",p:"...",t:"...",d:"...",w:N,h:N}
    # Parse by balancing {}.
    inner = feat_arr_str[1:-1]  # strip outer brackets
    items = []
    k = 0
    while k < len(inner):
        if inner[k] != '{':
            k += 1
            continue
        # Balance
        d = 0; start_k = k; in_s = None
        while k < len(inner):
            c = inner[k]
            if in_s:
                if c == '\\': k += 2; continue
                if c == in_s: in_s = None
            else:
                if c in ('"',"'"): in_s = c
                elif c == '{': d += 1
                elif c == '}':
                    d -= 1
                    if d == 0:
                        items.append(inner[start_k:k+1])
                        k += 1
                        break
            k += 1

    if not items:
        cursor = block_end; continue

    # Extract the `p:"..."` path from each item to compute sort key
    keyed = []
    for idx, it in enumerate(items):
        pm = re.search(r'p:"([^"]+)"', it)
        if not pm:
            keyed.append((section_key('',idx), idx, it))
        else:
            keyed.append((section_key(pm.group(1), idx), idx, it))

    # Stable sort by computed key
    keyed.sort(key=lambda x: x[0])

    # If order unchanged, skip
    new_order_indices = [orig_idx for _, orig_idx, _ in keyed]
    if new_order_indices == list(range(len(items))):
        cursor = block_end; continue

    # Rebuild feat array keeping the block's newline separator pattern
    sep = ',\n'
    new_feat = '[\n' + sep.join(it for _, _, it in keyed) + '\n]'

    # Replace in block
    new_block = block[:fs] + new_feat + block[fe:]
    updates.append((block_start, block_end, new_block, code, len(items)))

    cursor = block_end

# Apply updates in reverse so earlier positions don't shift
for block_start, block_end, new_block, code, n in reversed(updates):
    html = html[:block_start] + new_block + html[block_end:]

with open(HTML,'w',encoding='utf-8') as f: f.write(html)

print(f'Re-sorted features for {len(updates)} products:')
for _, _, _, code, n in updates:
    print(f'  {code:15s}  ({n} features)')
