#!/usr/bin/env python3
"""
Emergency cleanup: remove ALL product objects inserted outside const P array.
These orphaned objects cause JS parse errors that break the entire page.
"""
from pathlib import Path
import re

def find_const_p_bounds(content):
    start = content.find('const P=[')
    if start < 0:
        return -1, -1
    i = start + 9
    depth = 1
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
                    return start, i
        i += 1
    return -1, -1

def main():
    html_path = Path("C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html")
    content = html_path.read_text(encoding='utf-8')
    original_size = len(content)

    print(f"Original file size: {original_size:,} chars")

    # Find const P array bounds
    arr_start, arr_end = find_const_p_bounds(content)
    print(f"const P array: {arr_start:,} to {arr_end:,}")

    # Get product IDs that are OUTSIDE the array
    all_ids = re.findall(r'id:"([^"]+)"', content)
    ids_in_array = set(re.findall(r'id:"([^"]+)"', content[arr_start:arr_end+2]))

    orphaned_ids = []
    for pid in all_ids:
        if pid not in ids_in_array:
            orphaned_ids.append(pid)

    orphaned_ids = list(dict.fromkeys(orphaned_ids))  # dedupe, preserve order
    print(f"Orphaned product IDs outside array: {len(orphaned_ids)}")
    for pid in orphaned_ids:
        print(f"  - {pid}")

    # Split content into: before array, array itself, after array
    before_array = content[:arr_start]
    array_content = content[arr_start:arr_end+2]  # includes ];
    after_array = content[arr_end+2:]

    print(f"\nAfter array section length: {len(after_array):,} chars")

    # Remove ALL product object definitions from the "after array" section
    # A product object starts with {id:" and ends after the md:` ... ` field
    # Pattern: {id:"...", ..., md:`...`}
    # We need to handle nested backtick strings carefully

    # Strategy: find each {id:"..." block and remove it
    # Use a state machine to find complete product objects

    def remove_product_objects(text):
        """Remove all {id:"..." product objects from text"""
        result = []
        i = 0
        removed_count = 0

        while i < len(text):
            # Look for start of product object: {id:"
            idx = text.find('{id:"', i)
            if idx == -1:
                result.append(text[i:])
                break

            # Add everything before this product object
            result.append(text[i:idx])

            # Now find the matching closing } by tracking depth
            # but be careful with template literals
            j = idx
            depth = 0
            in_str = False
            sc = ''
            esc = False

            while j < len(text):
                c = text[j]
                if esc:
                    esc = False
                    j += 1
                    continue
                if c == '\\':
                    esc = True
                    j += 1
                    continue
                if in_str:
                    if c == sc:
                        in_str = False
                else:
                    if c in ('"', "'", '`'):
                        in_str = True
                        sc = c
                    elif c == '{':
                        depth += 1
                    elif c == '}':
                        depth -= 1
                        if depth == 0:
                            # End of product object found
                            removed_count += 1
                            # Skip optional leading comma
                            end_pos = j + 1
                            i = end_pos
                            break
                j += 1
            else:
                # Didn't find matching }
                result.append(text[idx:])
                break

        return ''.join(result), removed_count

    cleaned_after, removed = remove_product_objects(after_array)
    print(f"\nRemoved {removed} product objects from after-array section")
    print(f"After section: {len(after_array):,} -> {len(cleaned_after):,} chars")

    # Also clean before array (shouldn't have products but check)
    cleaned_before, removed_before = remove_product_objects(before_array)
    if removed_before:
        print(f"Also removed {removed_before} from before-array section")

    # Reconstruct file
    new_content = cleaned_before + array_content + cleaned_after
    print(f"\nNew file size: {len(new_content):,} chars (was {original_size:,})")

    # Verify
    new_arr_start, new_arr_end = find_const_p_bounds(new_content)
    new_array = new_content[new_arr_start:new_arr_end+2]
    count_in_array = new_array.count('id:"')
    total_in_file = new_content.count('id:"')

    print(f"Products in const P: {count_in_array}")
    print(f"Total id: in file: {total_in_file}")
    print(f"Orphaned (should be 0): {total_in_file - count_in_array}")

    if total_in_file != count_in_array:
        print("[WARNING] Still have orphaned products — NOT writing file")
        return False

    # Write
    html_path.write_text(new_content, encoding='utf-8')
    print(f"\n[SUCCESS] File cleaned and saved!")
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
