import re
with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_18.html','r',encoding='utf-8') as f:
    html = f.read()
# Find const PRODUCTS / P / PRODS etc
m = re.search(r'(?:const|let|var)\s+(\w+)\s*=\s*\[\s*\{id:"', html)
if not m:
    print('No product array found')
    raise SystemExit
start_marker_pos = m.start()
bracket_start = html.find('[', start_marker_pos)
# Scan to find matching ]
depth = 0
i = bracket_start
in_str = None
while i < len(html):
    c = html[i]
    if in_str:
        if c == '\\':
            i += 2
            continue
        if c == in_str:
            in_str = None
    else:
        if c in ('"', "'"): in_str = c
        elif c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                break
    i += 1
end = i + 1
snippet = html[bracket_start:end]
print(f'Array {bracket_start}..{end}, size={end-bracket_start:,}')
with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/_parse_test.js','w',encoding='utf-8') as f:
    f.write('const P=' + snippet + ';\nconsole.log("count=",P.length);\n')
