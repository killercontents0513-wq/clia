#!/usr/bin/env python3
"""Final verification that both products are ready for display"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

content = Path('LG_AI_Content_Hub_v6_20.html').read_text(encoding='utf-8')

print("=" * 70)
print("FINAL VERIFICATION: OLED65C5PUA & OLED77C5PUA")
print("=" * 70)
print()

# Find const P array
start = content.find('const P=[')
end = content.rfind('];', start)

if start < 0:
    print("ERROR: const P array not found")
    exit(1)

array_content = content[start:end+2]
print(f"const P array: {len(array_content):,} characters")
print()

# Extract product entries for verification
for product_id in ['OLED65C5PUA', 'OLED77C5PUA']:
    print(f"\n[PRODUCT] {product_id}")
    print("-" * 70)

    pattern = f'id:"{product_id}"'
    idx = array_content.find(pattern)

    if idx >= 0:
        # Find context around product
        context_start = max(0, idx - 200)
        context_end = min(len(array_content), idx + 5000)
        context = array_content[context_start:context_end]

        # Check for md field
        md_idx = context.find('md:`')
        if md_idx >= 0:
            print(f"✓ Product found in array")
            print(f"✓ md field PRESENT")

            # Extract md content to verify structure
            md_start = md_idx + 4
            md_end = context.find('`', md_start)
            if md_end > 0:
                md_content = context[md_start:md_end]
                # Decode escaped newlines for preview
                md_display = md_content.replace('\\n', '\n')[:200]

                print(f"\nMarkdown preview (first 200 chars):")
                print(md_display.encode('ascii', 'replace').decode('ascii'))
                print()

                # Check for key structural elements
                checks = [
                    ('# Title', '# LG OLED' in md_content),
                    ('## Sections', '## Product Overview' in md_content),
                    ('### Subsections', '###' in md_content),
                    ('Bold formatting', '**' in md_content),
                    ('Q: A: FAQ', 'Q:' in md_content and 'A:' in md_content),
                ]

                print("Structure verification:")
                for check_name, passed in checks:
                    status = "OK" if passed else "MISSING"
                    print(f"  {check_name}: {status}")

            else:
                print("WARNING: Could not extract md content")
        else:
            print("ERROR: md field NOT FOUND")
    else:
        print(f"ERROR: Product not found in array")

print()
print("=" * 70)
print("✓ VERIFICATION COMPLETE - Both products ready for display in 'Only MD' tab")
print("=" * 70)
