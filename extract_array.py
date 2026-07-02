import re
with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_18.html','r',encoding='utf-8') as f:
    html=f.read()
start = html.find('const P=[')
if start < 0:
    raise SystemExit('No const P=[ found')
bracket_start = html.find('[', start)
depth=0
i=bracket_start
in_str=None
while i<len(html):
    c=html[i]
    if in_str:
        if c=='\\':
            i+=2
            continue
        if c==in_str:
            in_str=None
    else:
        if c=='"' or c=="'":
            in_str=c
        elif c=='[':
            depth+=1
        elif c==']':
            depth-=1
            if depth==0:
                break
    i+=1
end=i+1
snip=html[bracket_start:end]
print('Array span', bracket_start, end, 'size=', end-bracket_start)
with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/_parse_test.js','w',encoding='utf-8') as f:
    f.write('const P=')
    f.write(snip)
    f.write(';\nconsole.log("count=",P.length);\n')
