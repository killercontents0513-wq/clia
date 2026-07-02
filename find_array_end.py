#!/usr/bin/env python3
"""Find the exact end of const P array"""
content = open('LG_AI_Content_Hub_v6_20.html', encoding='utf-8').read()

start_idx = content.find('const P=[')
print('const P=[ at char:', start_idx)

i = start_idx + 9  # skip 'const P=['
depth = 1  # We're already inside the [
in_str = False
sc = ''
escaped = False

while i < len(content):
    c = content[i]

    if escaped:
        escaped = False
        i += 1
        continue

    if c == '\\':
        escaped = True
        i += 1
        continue

    if in_str:
        if c == sc:
            in_str = False
    else:
        if c in ('"', "'", '`'):
            in_str = True
            sc = c
        elif c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                print('Closing ] at char:', i)
                print('Context before:', repr(content[i-50:i+5]))
                print('Next 10 chars:', repr(content[i:i+10]))
                break
    i += 1
