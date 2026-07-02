#!/usr/bin/env python3
"""
MD-Only List 전체 88개 제품 확장 생성
"""
import json
from pathlib import Path
from datetime import datetime

# 모든 88개 제품 목록
ALL_PRODUCTS = {
    "TV - OLED C5": [
        {"code": "OLED42C5PUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled42c5pua/", "type": "42-inch C5"},
        {"code": "OLED48C5PUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled48c5pua/", "type": "48-inch C5"},
        {"code": "OLED55C5PUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled55c5pua/", "type": "55-inch C5"},
        {"code": "OLED65C5PUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled65c5pua/", "type": "65-inch C5"},
        {"code": "OLED77C5PUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled77c5pua/", "type": "77-inch C5"},
        {"code": "OLED83C5PUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled83c5pua/", "type": "83-inch C5"},
        {"code": "OLED65C5YUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled65c5yua/", "type": "65-inch C5 YUA"},
        {"code": "OLED77C5YUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled77c5yua/", "type": "77-inch C5 YUA"},
    ],
    "TV - OLED G5": [
        {"code": "OLED55G5SUB", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled55g5sub/", "type": "55-inch G5 SUB"},
        {"code": "OLED55G5WUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled55g5wua/", "type": "55-inch G5 WUA"},
        {"code": "OLED65G5SUB", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled65g5sub/", "type": "65-inch G5 SUB"},
        {"code": "OLED65G5WUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled65g5wua/", "type": "65-inch G5 WUA"},
        {"code": "OLED77G5WUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled77g5wua/", "type": "77-inch G5 WUA"},
        {"code": "OLED83G5WUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled83g5wua/", "type": "83-inch G5 WUA"},
        {"code": "OLED97G5WUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled97g5wua/", "type": "97-inch G5 WUA"},
    ],
    "TV - OLED B5": [
        {"code": "OLED48B5PUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled/oled48b5pua/", "type": "48-inch B5"},
        {"code": "OLED55B5PUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled/oled55b5pua/", "type": "55-inch B5"},
        {"code": "OLED65B5PUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled/oled65b5pua/", "type": "65-inch B5"},
        {"code": "OLED77B5PUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled/oled77b5pua/", "type": "77-inch B5"},
        {"code": "OLED83B5PUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled/oled83b5pua/", "type": "83-inch B5"},
    ],
    "TV - OLED G6": [
        {"code": "OLED55G6SUB", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled55g6sub/", "type": "55-inch G6 SUB"},
        {"code": "OLED65G6SUB", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled65g6sub/", "type": "65-inch G6 SUB"},
        {"code": "OLED65G6WUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled65g6wua/", "type": "65-inch G6 WUA"},
        {"code": "OLED77G6WUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled77g6wua/", "type": "77-inch G6 WUA"},
        {"code": "OLED83G6WUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled83g6wua/", "type": "83-inch G6 WUA"},
    ],
    "TV - OLED C6": [
        {"code": "OLED65C6PUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled65c6pua/", "type": "65-inch C6"},
        {"code": "OLED77C6HUP", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled77c6hup/", "type": "77-inch C6 HUP"},
        {"code": "OLED83C6HUP", "url": "https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled83c6hup/", "type": "83-inch C6 HUP"},
    ],
    "TV - OLED Other": [
        {"code": "OLED77T4PUA", "url": "https://www.lg.com/ca_en/tv-soundbars/oled/oled77t4pua/", "type": "77-inch T4"},
        {"code": "OLED77G6P", "url": "https://www.lg.com/ca_en/tv-soundbars/oled/oled77g6p/", "type": "77-inch G6 P"},
    ],
    "Refrigerators - French Door": [
        {"code": "LF20C6330S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lf20c6330s/", "type": "20 cu.ft"},
        {"code": "LF21C6200S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lf21c6200s/", "type": "21 cu.ft"},
        {"code": "LF24C8200S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lf24c8200s/", "type": "24 cu.ft"},
        {"code": "LF24Z6530S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lf24z6530s/", "type": "24 cu.ft Z6530"},
        {"code": "LF25H6200S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lf25h6200s/", "type": "25 cu.ft"},
        {"code": "LF25H6330S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lf25h6330s/", "type": "25 cu.ft H6330"},
        {"code": "LF25S6200S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lf25s6200s/", "type": "25 cu.ft S6200"},
        {"code": "LF25S6330S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lf25s6330s/", "type": "25 cu.ft S6330"},
        {"code": "LF25S6560S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lf25s6560s/", "type": "25 cu.ft S6560"},
        {"code": "LF25Z6211S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lf25z6211s/", "type": "25 cu.ft Z6211"},
        {"code": "LF29S8365S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lf29s8365s/", "type": "29 cu.ft"},
        {"code": "LF30S8210S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lf30s8210s/", "type": "30 cu.ft"},
        {"code": "LRFLC2706S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lrflc2706s/", "type": "27 cu.ft"},
        {"code": "LRFLS3206S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lrfls3206s/", "type": "32 cu.ft"},
        {"code": "LRFNS2200S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lrfns2200s/", "type": "22 cu.ft"},
        {"code": "LRFS28XBS", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lrfs28xbs/", "type": "28 cu.ft"},
        {"code": "LRFWS2200S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lrfws2200s/", "type": "22 cu.ft"},
        {"code": "LRFXC2606S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lrfxc2606s/", "type": "26 cu.ft"},
        {"code": "LRYXC2606S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lryxc2606s/", "type": "26 cu.ft"},
        {"code": "LRYXS3106S", "url": "https://www.lg.com/ca_en/refrigerators/french-door/lryxs3106s/", "type": "31 cu.ft"},
        {"code": "SRFB27S3", "url": "https://www.lg.com/ca_en/refrigerators/french-door/srfb27s3/", "type": "27 cu.ft (Stainless)"},
        {"code": "SRFB27W3", "url": "https://www.lg.com/ca_en/refrigerators/french-door/srfb27w3/", "type": "27 cu.ft (White)"},
    ],
    "Refrigerators - Bottom Freezer": [
        {"code": "LBNC12231V", "url": "https://www.lg.com/ca_en/refrigerators/bottom-freezer/lbnc12231v/", "type": "12 cu.ft"},
        {"code": "LBNC15251V", "url": "https://www.lg.com/ca_en/refrigerators/bottom-freezer/lbnc15251v/", "type": "15 cu.ft"},
        {"code": "LRDNS2200S", "url": "https://www.lg.com/ca_en/refrigerators/bottom-freezer/lrdns2200s/", "type": "22 cu.ft"},
    ],
    "Refrigerators - One Door": [
        {"code": "LROFC1104V", "url": "https://www.lg.com/ca_en/refrigerators/one-door/lrofc1104v/", "type": "11 cu.ft"},
        {"code": "LRONC1404V", "url": "https://www.lg.com/ca_en/refrigerators/one-door/lronc1404v/", "type": "14 cu.ft"},
    ],
    "Refrigerators - Kimchi": [
        {"code": "LK12S6000V", "url": "https://www.lg.com/ca_en/refrigerators/kimchi-specialty/lk12s6000v/", "type": "12 cu.ft Specialty"},
        {"code": "LK14S8000V", "url": "https://www.lg.com/ca_en/refrigerators/kimchi/lk14s8000v/", "type": "14 cu.ft"},
    ],
    "Laundry - Washers": [
        {"code": "WM1455HWA", "url": "https://www.lg.com/ca_en/laundry/washers/wm1455hwa/", "type": "Front Load"},
        {"code": "WM3400CV", "url": "https://www.lg.com/ca_en/laundry/washers/wm3400cv/", "type": "Front Load"},
        {"code": "WM3400CW", "url": "https://www.lg.com/ca_en/laundry/washers/wm3400cw/", "type": "Front Load"},
        {"code": "WM3470CW", "url": "https://www.lg.com/ca_en/laundry/washers/wm3470cw/", "type": "Front Load"},
        {"code": "WM3580CX", "url": "https://www.lg.com/ca_en/laundry/washers/wm3580cx/", "type": "Front Load"},
        {"code": "WM3600HVA", "url": "https://www.lg.com/ca_en/laundry/washers/wm3600hva/", "type": "Front Load"},
        {"code": "WM3600HWA", "url": "https://www.lg.com/ca_en/laundry/washers/wm3600hwa/", "type": "Front Load"},
        {"code": "WM3850HVA", "url": "https://www.lg.com/ca_en/laundry/washers/wm3850hva/", "type": "Front Load"},
        {"code": "WM4100HBA", "url": "https://www.lg.com/ca_en/laundry/washers/wm4100hba/", "type": "Front Load"},
        {"code": "WM4100HWA", "url": "https://www.lg.com/ca_en/laundry/washers/wm4100hwa/", "type": "Front Load"},
        {"code": "WM5500HVA", "url": "https://www.lg.com/ca_en/laundry/washers/wm5500hva/", "type": "Front Load"},
        {"code": "WM5800HVA", "url": "https://www.lg.com/ca_en/laundry/washers/wm5800hva/", "type": "Front Load"},
        {"code": "WM6500HBA", "url": "https://www.lg.com/ca_en/laundry/washers/wm6500hba/", "type": "Front Load"},
        {"code": "WM6700HBA", "url": "https://www.lg.com/ca_en/laundry/washers/wm6700hba/", "type": "Front Load"},
        {"code": "WM8900HBA", "url": "https://www.lg.com/ca_en/laundry/washers/wm8900hba/", "type": "Front Load"},
        {"code": "WT6105CW", "url": "https://www.lg.com/ca_en/laundry/washers/wt6105cw/", "type": "Top Load"},
        {"code": "WT7010CW", "url": "https://www.lg.com/ca_en/laundry/washers/wt7010cw/", "type": "Top Load"},
        {"code": "WT8200CW", "url": "https://www.lg.com/ca_en/laundry/washers/wt8200cw/", "type": "Top Load"},
        {"code": "WT8205CW", "url": "https://www.lg.com/ca_en/laundry/washers/wt8205cw/", "type": "Top Load"},
        {"code": "WT8400CB", "url": "https://www.lg.com/ca_en/laundry/washers/wt8400cb/", "type": "Top Load"},
        {"code": "WT8400CW", "url": "https://www.lg.com/ca_en/laundry/washers/wt8400cw/", "type": "Top Load"},
        {"code": "WT8405CB", "url": "https://www.lg.com/ca_en/laundry/washers/wt8405cb/", "type": "Top Load"},
        {"code": "WT8405CW", "url": "https://www.lg.com/ca_en/laundry/washers/wt8405cw/", "type": "Top Load"},
        {"code": "WT8600CB", "url": "https://www.lg.com/ca_en/laundry/washers/wt8600cb/", "type": "Top Load"},
        {"code": "WD6700-B", "url": "https://www.lg.com/ca_en/laundry/washers/wd6700-b/", "type": "Top Load"},
    ],
    "Laundry - Washer-Dryer Combos": [
        {"code": "WKE100HWA", "url": "https://www.lg.com/ca_en/laundry/washer-dryer-combos/wke100hwa/", "type": "Combo"},
        {"code": "WKEX200HWA", "url": "https://www.lg.com/ca_en/laundry/washer-dryer-combos/wkex200hwa/", "type": "Combo"},
        {"code": "WKGX201HBA", "url": "https://www.lg.com/ca_en/laundry/washer-dryer-combos/wkgx201hba/", "type": "Combo"},
        {"code": "WM3555HVA", "url": "https://www.lg.com/ca_en/laundry/washer-dryer-combos/wm3555hva/", "type": "Combo"},
        {"code": "WM6998HBA", "url": "https://www.lg.com/ca_en/laundry/washer-dryer-combos/wm6998hba/", "type": "Combo"},
    ],
}

def create_md_template_simple(code, ptype):
    """Create markdown template"""
    template = f"""# LG {ptype} — {code} | LG Canada

## Product Overview

The LG {code} is designed for Canadian households. [Content to be extracted from PDP]

## Key Features

### Feature 1: Benefit
- Details with specifications

### Feature 2: Advanced Technology
- Details with measurements

## Technical Specifications

- **Model:** {code}
- **Market:** Canada

## Who It's For

- User profile 1
- User profile 2
- User profile 3

## Frequently Asked Questions

**Q: What are the key features?**
A: [To be populated from PDP]

**Q: What is the warranty coverage?**
A: Standard LG Canada warranty applies.

---
**Status:** Pending PDP extraction | **Category:** {ptype.split()[0]} | **Created:** {datetime.now().strftime('%Y-%m-%d')}
"""
    return template

def main():
    output_dir = Path("C:/Users/Administrator/Desktop/AI/RetailOBS/3P/MD-ONLY-LIST")
    output_dir.mkdir(exist_ok=True)

    total = 0
    stats = {}

    for category, products in ALL_PRODUCTS.items():
        cat_count = 0
        for product in products:
            code = product["code"]
            ptype = product["type"]

            # Create markdown
            md_file = output_dir / f"{code.lower()}-product-info.md"
            md_file.write_text(create_md_template_simple(code, ptype), encoding='utf-8')

            # Create metadata
            meta = {
                "code": code,
                "url": product["url"],
                "type": ptype,
                "status": "pending_pdp_extraction",
                "created": datetime.now().isoformat()
            }
            meta_file = output_dir / f"{code}-metadata.json"
            meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')

            total += 1
            cat_count += 1
            print(f"[OK] {code}")

        stats[category] = cat_count
        print(f"    {category}: {cat_count} products")

    # Create summary
    summary = f"""# MD-Only List Expansion — Complete

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Total Products:** {total}

## Breakdown by Category

"""
    for cat, count in stats.items():
        summary += f"- {cat}: {count}\n"

    summary += f"""
## Files Created

- {total} markdown template files ({code.lower()}-product-info.md)
- {total} metadata JSON files ({code}-metadata.json)
- Total: {total*2} files

## Next Steps

1. **PDP Content Extraction**
   - Visit each LG Canada PDP URL
   - Extract product description, specs, features
   - Use WebFetch tool or Chrome extension

2. **Markdown Population**
   - Fill in Product Overview with actual specs
   - Add Key Features with quantified benefits
   - Complete Technical Specifications
   - Add relevant certifications

3. **Analysis Documents**
   - Create {code}-MD-ANALYSIS.md for each
   - Track compliance with geo_markdown_guide.md
   - Add citation optimization notes

## Quality Checklist

For each product, ensure:
- [ ] Minimum 2 quantified specs in Product Overview
- [ ] Key Features with "Benefit: Metric" format
- [ ] Technical Specs with units (mm, kg, W, etc.)
- [ ] 3-5 "Who It's For" personas
- [ ] 5-10 FAQ questions
- [ ] Certifications/Awards (if applicable)
- [ ] No marketing fluff, only facts

"""

    summary_file = output_dir / "EXPANSION_SUMMARY.md"
    summary_file.write_text(summary, encoding='utf-8')

    print(f"\n[COMPLETE] {total} products created")
    print(f"[SUMMARY] {summary_file}")

if __name__ == '__main__':
    main()
