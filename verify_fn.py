with open('C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_18.html','r',encoding='utf-8') as f:
    html = f.read()
s = html.index('function aplusAutoGenerate')
i = html.index('{', s)
depth = 0
in_str = None
in_tpl = False
start_fn = i
while i < len(html):
    c = html[i]
    if in_str:
        if c == '\\':
            i += 2
            continue
        if c == in_str:
            in_str = None
    elif in_tpl:
        if c == '\\':
            i += 2
            continue
        if c == '`':
            in_tpl = False
    else:
        if c == '"' or c == "'":
            in_str = c
        elif c == '`':
            in_tpl = True
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                print('Function spans', start_fn, '..', i+1, 'size=', i+1-start_fn)
                break
    i += 1
if depth != 0:
    print('UNBALANCED depth=', depth)
else:
    body = html[start_fn:i+1]
    for key in ['SLOT_TARGETS','scoreFit','dedupeFeats','Cinematic Banner','Landscape Hero','Key Highlights','Alt Feature','Grid / Summary']:
        print('Has', repr(key), ':', key in body)
