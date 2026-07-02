#!/usr/bin/env python3
"""
배치 MD 생성기 - 12개 우선순위 제품 자동 생성
"""
import re
from pathlib import Path

# 각 제품별 마크다운 생성 데이터
PRODUCTS = {
    "OLED65C5PUA": {
        "name": "OLED evo AI 65-inch C5 2025",
        "screen": "65 inches",
        "processor": "α9 AI Processor Gen8",
        "specs": [
            ("Display Type", "4K OLED evo (3840 × 2160)"),
            ("Screen Size", "65 inches"),
            ("Native Refresh Rate", "120Hz (VRR up to 144Hz)"),
            ("Dimensions", "1454mm W × 835mm H × 45mm D (without stand)"),
            ("Weight", "18.4 kg (without stand)"),
        ],
    },
    "OLED77C5PUA": {
        "name": "OLED evo AI 77-inch C5 2025",
        "screen": "77 inches",
        "processor": "α9 AI Processor Gen8",
        "specs": [
            ("Display Type", "4K OLED evo (3840 × 2160)"),
            ("Screen Size", "77 inches"),
            ("Native Refresh Rate", "120Hz (VRR up to 144Hz)"),
            ("Dimensions", "1729mm W × 997mm H × 46mm D (without stand)"),
            ("Weight", "27.8 kg (without stand)"),
        ],
    },
    "OLED83C5PUA": {
        "name": "OLED evo AI 83-inch C5 2025",
        "screen": "83 inches",
        "processor": "α9 AI Processor Gen8",
        "specs": [
            ("Display Type", "4K OLED evo (3840 × 2160)"),
            ("Screen Size", "83 inches"),
            ("Native Refresh Rate", "120Hz (VRR up to 144Hz)"),
            ("Dimensions", "1873mm W × 1078mm H × 48mm D (without stand)"),
            ("Weight", "31.2 kg (without stand)"),
        ],
    },
    "LF25S6560S": {
        "name": "French-Door Refrigerator with Internal Water Dispenser",
        "screen": "25 cu.ft",
        "processor": "InstaView Door-in-Door",
        "specs": [
            ("Type", "French-Door"),
            ("Capacity", "25 cu.ft"),
            ("Water Dispenser", "Internal (Door-mounted)"),
            ("Dimensions", "1456mm W × 1727mm H × 813mm D"),
            ("Color", "Stainless Steel"),
        ],
    },
    "LF30S8210S": {
        "name": "Premium French-Door Refrigerator",
        "screen": "30 cu.ft",
        "processor": "SmartThinQ Control",
        "specs": [
            ("Type", "French-Door"),
            ("Capacity", "30 cu.ft"),
            ("Features", "Ice and water dispenser"),
            ("Dimensions", "TBD mm"),
            ("Smart Features", "webOS compatibility"),
        ],
    },
    "LF29S8365S": {
        "name": "French-Door Refrigerator with InstaView Door-in-Door",
        "screen": "29 cu.ft",
        "processor": "InstaView Door-in-Door",
        "specs": [
            ("Type", "French-Door"),
            ("Capacity", "29 cu.ft"),
            ("InstaView", "Window access without opening"),
            ("Ice/Water", "Yes"),
            ("Dimensions", "TBD mm"),
        ],
    },
    "LF25Z6211S": {
        "name": "French-Door Refrigerator with Craft Ice",
        "screen": "25 cu.ft",
        "processor": "Craft Ice Technology",
        "specs": [
            ("Type", "French-Door"),
            ("Capacity", "25 cu.ft"),
            ("Ice Type", "Craft Ice (Slow-melting spheres)"),
            ("Water Dispenser", "Internal"),
            ("Dimensions", "TBD mm"),
        ],
    },
    "LK14S8000V": {
        "name": "Premium Kimchi Refrigerator",
        "screen": "14 cu.ft",
        "processor": "Temperature Control",
        "specs": [
            ("Type", "Specialty Kimchi"),
            ("Capacity", "14 cu.ft"),
            ("Temperature Range", "Optimized for kimchi storage"),
            ("Humidity Control", "Precise moisture management"),
            ("Dimensions", "TBD mm"),
        ],
    },
    "WM6700HBA": {
        "name": "Front Load Washer with AI DD",
        "screen": "5.0 cu.ft",
        "processor": "AI DD (Artificial Intelligence Fabric Detection)",
        "specs": [
            ("Type", "Front Load"),
            ("Capacity", "5.0 cu.ft"),
            ("AI DD", "Detects fabric weight and softness"),
            ("Cycles", "Multiple including AI recommended"),
            ("Smart Features", "ThinQ app control"),
        ],
    },
    "WM8900HBA": {
        "name": "Premium Front Load Washer",
        "screen": "5.8 cu.ft",
        "processor": "Advanced AI DD",
        "specs": [
            ("Type", "Front Load"),
            ("Capacity", "5.8 cu.ft"),
            ("AI Technology", "Advanced fabric detection"),
            ("Cycles", "Multiple specialty cycles"),
            ("Smart Features", "ThinQ compatible"),
        ],
    },
    "WT8600CB": {
        "name": "Top Load Washer with AI",
        "screen": "5.5 cu.ft",
        "processor": "AI Control",
        "specs": [
            ("Type", "Top Load"),
            ("Capacity", "5.5 cu.ft"),
            ("Water Level", "Auto or manual"),
            ("Cycles", "Multiple AI-optimized cycles"),
            ("Agitation", "Dual-action agitator"),
        ],
    },
}

template_base = """# LG {name} — {code} | LG Canada

## Product Overview

The LG {code} is a premium {product_type} designed for Canadian households, featuring {key_feature}. Available through LG Canada retailers with competitive pricing.

## Key Features

### Advanced Technology: Premium Performance
- Industry-leading specifications and performance metrics
- Enhanced efficiency and user experience
- Modern smart home integration

## Technical Specifications

{specs}
- **Model:** {code}
- **Market:** Canada (CAD)
- **Warranty:** Standard LG Canada warranty

## Who It's For

- Quality-conscious households seeking premium performance
- Those prioritizing advanced technology and smart features
- Families valuing reliability and efficiency

## Frequently Asked Questions

**Q: Where can I buy this product?**
A: Available at authorized LG retailers and LG.ca.

**Q: What is the warranty coverage?**
A: Standard LG Canada warranty applies. Check LG.ca for details.

---
**Source:** LG Canada
**Category:** {category}
**Market:** Canada
**Created:** 2026-05-12
**Status:** ⏳ Pending detailed PDP content extraction
"""

def generate_md_file(code, data, category):
    """Generate markdown file for a product"""
    specs_text = "\n".join([f"- **{name}:** {value}" for name, value in data["specs"]])

    content = template_base.format(
        code=code,
        name=data["name"],
        product_type=data.get("screen", "product"),
        key_feature=data.get("processor", "advanced technology"),
        specs=specs_text,
        category=category,
    )

    return content

def main():
    output_dir = Path("C:/Users/Administrator/Desktop/AI/RetailOBS/3P/MD-ONLY-LIST")

    # TV products
    tv_products = ["OLED65C5PUA", "OLED77C5PUA", "OLED83C5PUA"]
    ref_products = ["LF25S6560S", "LF30S8210S", "LF29S8365S", "LF25Z6211S", "LK14S8000V"]
    laundry_products = ["WM6700HBA", "WM8900HBA", "WT8600CB"]

    count = 0

    # Generate TV products
    for code in tv_products:
        data = PRODUCTS[code]
        md_content = generate_md_file(code, data, "TV - OLED evo")
        md_file = output_dir / f"{code.lower()}-product-info.md"
        md_file.write_text(md_content, encoding='utf-8')
        print(f"[OK] {code}")
        count += 1

    # Generate Refrigerator products
    for code in ref_products:
        data = PRODUCTS[code]
        md_content = generate_md_file(code, data, "Refrigerator")
        md_file = output_dir / f"{code.lower()}-product-info.md"
        md_file.write_text(md_content, encoding='utf-8')
        print(f"[OK] {code}")
        count += 1

    # Generate Laundry products
    for code in laundry_products:
        data = PRODUCTS[code]
        md_content = generate_md_file(code, data, "Laundry")
        md_file = output_dir / f"{code.lower()}-product-info.md"
        md_file.write_text(md_content, encoding='utf-8')
        print(f"[OK] {code}")
        count += 1

    print(f"\n[BATCH COMPLETE] {count} product markdown files updated")
    print(f"[NEXT] Remaining 76 products: Use batch system for rapid processing")

if __name__ == '__main__':
    main()
