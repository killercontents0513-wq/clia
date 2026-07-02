#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GEO Markdown Generator
JSON 크롤 데이터 → 마크다운 파일 자동 생성
기준: LG.COM GEO 마크다운 콘텐츠 작성 가이드 (2026.3.26)
"""

import json
import sys
import re
from pathlib import Path

def load_json(json_file):
    """Load crawl JSON data"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_category_mode_section(category):
    """Return mode section header based on category"""
    modes = {
        'TV': 'Picture & Sound Modes',
        'Monitor': 'Picture & Sound Modes',
        'Washer': 'Wash Cycles',
        'Dryer': 'Dry Cycles',
        'Refrigerator': 'Cooling Features',
        'Air Conditioner': 'Operating Modes',
        'Air Purifier': 'Fan & Filter Modes',
        'Dishwasher': 'Wash Programmes',
        'Audio': 'Operating Modes',
    }
    return modes.get(category, 'Operating Modes')

def sanitize_filename(code):
    """Convert model code to safe filename"""
    return code.lower().replace(' ', '-')

def generate_product_overview(data, category):
    """Generate Product Overview section"""
    overview = f"""## Product Overview

The LG {data.get('name', 'Product')} {data['code']} is a {category} product."""

    if data.get('gal'):
        overview += f"\nIt features {len(data['gal'])} high-quality gallery images"

    if data.get('feat'):
        overview += f" and {len(data['feat'])} detailed features."
    else:
        overview += "."

    overview += f"\nPrice: {data.get('price', 'N/A')} {data.get('currency', 'SAR')}"

    return overview

def generate_key_features(data):
    """Generate Key Features section from feat data"""
    if not data.get('feat') or len(data['feat']) == 0:
        return "## Key Features\n\n(No features data available)"

    features = "## Key Features\n\n"

    for i, feat in enumerate(data['feat'][:5], 1):  # Top 5 features
        title = feat.get('t', f"Feature {i}")
        desc = feat.get('d', '')

        # Format: "Feature: Benefit"
        features += f"### {title}\n"
        features += f"- {desc}\n\n"

    return features.rstrip()

def generate_technical_specs(data):
    """Generate Technical Specifications section"""
    specs = "## Technical Specifications\n\n"

    if data.get('sp') and isinstance(data['sp'], list):
        for spec in data['sp'][:10]:  # Top 10 specs
            if isinstance(spec, dict):
                name = spec.get('n', '')
                value = spec.get('v', '')
                specs += f"- **{name}:** {value}\n"
    else:
        specs += "- (Specifications data unavailable)\n"

    return specs

def generate_who_its_for(category):
    """Generate Who It's For section (template)"""
    templates = {
        'TV': """## Who It's For

- Viewers seeking the deepest black levels and highest contrast ratio.
- Gamers requiring low input lag and high refresh rates for competitive play.
- Home cinema enthusiasts wanting premium picture and sound quality.
- Those replacing a projector with a large-format flat panel.""",

        'Washer': """## Who It's For

- Households wanting to reduce fabric damage with smart wash technology.
- Families with allergy sufferers needing steam sanitisation.
- Anyone managing various fabric types without manual cycle selection.
- Those seeking energy efficiency and reduced water consumption.""",

        'Audio': """## Who It's For

- Music enthusiasts and party-goers seeking powerful, immersive sound.
- DJs and content creators needing professional-grade mixing and effects.
- Those wanting karaoke and wireless connectivity features.
- Anyone prioritising premium audio quality and LED visual effects.""",
    }

    return templates.get(category, """## Who It's For

- [Specific user profile 1]
- [Specific user profile 2]
- [Specific user profile 3]
- [Specific user profile 4]""")

def generate_faq(data):
    """Generate FAQ section (template)"""
    faq = f"""## Frequently Asked Questions

**Q: What is the {data['code']}?**
A: The {data['code']} is a premium product from LG designed for discerning users seeking quality and performance.

**Q: Does it include warranty?**
A: Yes. Please refer to LG.com for region-specific warranty information.

**Q: Where can I buy the {data['code']}?**
A: The {data['code']} is available at authorized LG retailers and the official LG website.

**Q: What is the price?**
A: The {data['code']} is priced at {data.get('price', 'contact for pricing')} {data.get('currency', 'SAR')}.

**Q: Is this product energy efficient?**
A: Yes. LG products are designed with efficiency in mind. Check the product specifications for detailed energy ratings."""

    return faq

def generate_markdown(data, category='Audio'):
    """Main markdown generation function"""

    code = data.get('code', 'UNKNOWN')
    name = data.get('name', code)

    # H1
    md = f"# LG {name} — {code} | LG Saudi Arabia\n\n"

    # Product Overview
    md += generate_product_overview(data, category) + "\n\n"

    # Key Features
    md += generate_key_features(data) + "\n\n"

    # Technical Specifications
    md += generate_technical_specs(data) + "\n\n"

    # Mode Section (category-specific)
    mode_header = get_category_mode_section(category)
    md += f"## {mode_header}\n\n"
    md += "(Modes/cycles data to be added from PDP specifications)\n\n"

    # Who It's For
    md += generate_who_its_for(category) + "\n\n"

    # FAQ
    md += generate_faq(data) + "\n"

    return md

def main():
    """Main execution"""

    if len(sys.argv) < 2:
        print("[Usage] python generate_markdown.py <json_file> [category]")
        print("[Example] python generate_markdown.py rnc7_data.json Audio")
        sys.exit(1)

    json_file = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else 'Audio'

    # Load JSON
    try:
        data = load_json(json_file)
    except FileNotFoundError:
        print(f"[FAIL] File not found: {json_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[FAIL] Invalid JSON: {e}")
        sys.exit(1)

    code = data.get('code', 'unknown')

    # Generate markdown
    print(f"[OK] Loaded {code} from {json_file}")
    md_content = generate_markdown(data, category)

    # Save markdown
    md_filename = f"{sanitize_filename(code)}-product-info.md"
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"[OK] Generated: {md_filename}")
    print(f"\n=== GENERATED MARKDOWN ===\n{md_content[:500]}...\n")

    return 0

if __name__ == '__main__':
    sys.exit(main())
