import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P'
with open(f'{BASE}/LG_AI_Content_Hub_v6_18.html','r',encoding='utf-8',errors='replace') as f:
    html = f.read()
idx = html.find('id:"RH81T2SP7RM"')
start = html.rfind('{', 0, idx)
depth=0; i=start
while i<len(html):
    if html[i]=='{': depth+=1
    elif html[i]=='}':
        depth-=1
        if depth==0: break
    i+=1
entry = html[start:i+1]
print(f'Entry size: {len(entry)} chars')
print(entry[:3000])
