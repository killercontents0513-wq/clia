#!/usr/bin/env python3
"""
Fix const P array closing in v6_20.html
The array was not properly terminated during integration
"""
import re
from pathlib import Path

def fix_const_p_array():
    v6_20_file = Path("C:/Users/Administrator/Desktop/AI/RetailOBS/3P/LG_AI_Content_Hub_v6_20.html")

    if not v6_20_file.exists():
        print("[ERROR] v6_20.html not found")
        return False

    # Read file
    content = v6_20_file.read_text(encoding='utf-8')

    # Find the problematic pattern: `},8000);
    # This should be replaced with just: }];

    # Find the last occurrence of },8000);
    problem_pattern = "},8000);"
    if problem_pattern not in content:
        print("[ERROR] Problem pattern not found. Array might already be fixed.")
        return False

    # Replace the last occurrence
    last_index = content.rfind(problem_pattern)
    if last_index > 0:
        # Replace },8000); with }];
        new_content = content[:last_index] + "}];" + content[last_index + len(problem_pattern):]

        # Write back
        v6_20_file.write_text(new_content, encoding='utf-8')

        print("[SUCCESS] Fixed const P array closing bracket")
        print("  - Replaced: },8000);")
        print("  - With: }];")

        # Verify
        if "}];" in new_content and "},8000);" not in new_content:
            print("[VERIFIED] Array closure is correct")
            return True
        else:
            print("[WARNING] Verification failed")
            return False

    return False

if __name__ == '__main__':
    fix_const_p_array()
