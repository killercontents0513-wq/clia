"""Inspect RH81T2SP7RM in Apr 20 backup."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'

# Try all Apr 20 backups from latest to earliest
apr20_files = [
    'LG_AI_Content_Hub_v6_18.pre_A9K-SOLO.html',
    'LG_AI_Content_Hub_v6_18.pre_WFR1114MB.html',
    'LG_AI_Content_Hub_v6_18.pre_S20A.html',
    'LG_AI_Content_Hub_v6_18.pre_S65TR.html',
    'LG_AI_Content_Hub_v6_18.pre_WFN1310WHT.html',
    'LG_AI_Content_Hub_v6_18.pre_LS25CBBDIK.html',
    'LG_AI_Content_Hub_v6_18.pre_WFN1310BST.html',
]

for fname in apr20_files:
    with open(f'{BASE}/{fname}','r',encoding='utf-8',errors='replace') as f:
        html = f.read()
    idx = html.find('id:"RH81T2SP7RM"')
    if idx < 0: idx = html.find("id:'RH81T2SP7RM'")
    if idx < 0:
        print(f'{fname}: NOT FOUND')
        continue
    # Get the block
    start = html.rfind('{', 0, idx)
    depth = 0
    i = start
    while i < len(html):
        c = html[i]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: break
        i += 1
    entry = html[start:i+1]

    # Count gal/feat images
    n_gal = len(re.findall(r'"p"\s*:', entry))  # old style
    n_gal2 = entry.count('p:"') + entry.count("p:'")  # new style
    print(f'\n{fname} (entry={len(entry)}b):')
    print(f'  "p": count={n_gal}, p: count={n_gal2}')
    # Show first 600 chars
    print(entry[:600])
    print('  ...')
    break  # just first found
