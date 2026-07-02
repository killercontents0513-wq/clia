#!/usr/bin/env python3
"""
SAFE cleanup: only remove orphaned product objects from AFTER the const P array.
NEVER touch before-array content (it contains embedded JS/base64 that looks like products).
"""
from pathlib import Path
import re

def find_const_p_bounds(content):
    start = content.find('const P=[')
    if start < 0:
        return -1, -1
    i = start + 9
    depth = 1
    in_str = False; sc = ''; escaped = False
    while i < len(content):
        c = content[i]
        if escaped: escaped=False; i+=1; continue
        if c == '\\': escaped=True; i+=1; continue
        if in_str:
            if c == sc: in_str=False
        else:
            if c in ('"', "'", '`'): in_str=True; sc=c
            elif c == '[': depth+=1
            elif c == ']':
                depth-=1
                if depth==0: return start, i
        i+=1
    return -1, -1

def remove_product_objects_from_after(after_text):
    """
    Remove standalone product objects {id:"...", ..., md:`...`} from after-array text.
    These are orphaned objects inserted by broken integration scripts.
    """
    result = []
    i = 0
    removed = 0

    while i < len(after_text):
        idx = after_text.find('{id:"', i)
        if idx == -1:
            result.append(after_text[i:])
            break

        # Verify this looks like a product (has md: or mdAnalysis:)
        preview = after_text[idx:idx+200]
        if 'md:`' not in preview and 'mdAnalysis:`' not in preview:
            result.append(after_text[i:idx+5])
            i = idx + 5
            continue

        # Save everything before this product
        result.append(after_text[i:idx])

        # Find the matching closing } using bracket+string tracking
        j = idx
        depth = 0
        in_str = False; sc = ''; escaped = False

        while j < len(after_text):
            c = after_text[j]
            if escaped: escaped=False; j+=1; continue
            if c == '\\': escaped=True; j+=1; continue
            if in_str:
                if c == sc: in_str=False
            else:
                if c in ('"', "'", '`'): in_str=True; sc=c
                elif c == '{': depth+=1
                elif c == '}':
                    depth-=1
                    if depth==0:
                        removed+=1
                        i = j+1
                        break
            j+=1
        else:
            result.append(after_text[idx:])
            break

    return ''.join(result), removed

def main():
    html = Path('LG_AI_Content_Hub_v6_20.html')
    content = html.read_text(encoding='utf-8')
    print(f'File: {len(content):,} chars')

    arr_start, arr_end = find_const_p_bounds(content)
    print(f'const P: {arr_start:,} to {arr_end:,}')

    before_array = content[:arr_start]
    array_content = content[arr_start:arr_end+2]
    after_array  = content[arr_end+2:]

    # Count what's in array vs outside
    ids_in_array = set(re.findall(r'id:"([^"]+)"', array_content))
    ids_before   = re.findall(r'id:"([^"]+)"', before_array)
    ids_after    = re.findall(r'id:"([^"]+)"', after_array)

    print(f'Products in array: {len(ids_in_array)}')
    print(f'id:" in before-array: {len(ids_before)} (leaving untouched)')
    print(f'id:" in after-array:  {len(ids_after)} (removing orphans)')

    # Only clean after-array
    cleaned_after, removed = remove_product_objects_from_after(after_array)
    print(f'Removed {removed} orphaned product objects from after-array')
    print(f'After section: {len(after_array):,} → {len(cleaned_after):,} chars')

    # Rebuild
    new_content = before_array + array_content + cleaned_after
    total_ids = new_content.count('id:"')
    print(f'New file: {len(new_content):,} chars, total id": {total_ids}')

    # Verify renderList is still present
    assert 'function renderList' in new_content, 'renderList MISSING!'
    print('renderList: present ✓')

    html.write_text(new_content, encoding='utf-8')
    print('\n[SUCCESS] Safely cleaned after-array only.')

if __name__ == '__main__':
    main()
