"""Show full RH81T2SP7RM from Apr 20 backup."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
with open(f'{BASE}/LG_AI_Content_Hub_v6_18.pre_A9K-SOLO.html','r',encoding='utf-8',errors='replace') as f:
    html = f.read()
idx = html.find('id:"RH81T2SP7RM"')
start = html.rfind('{', 0, idx)
depth = 0; i = start
while i < len(html):
    c = html[i]
    if c == '{': depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0: break
    i += 1
entry = html[start:i+1]
print(entry)
