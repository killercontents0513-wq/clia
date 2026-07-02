# Product Management Lists — Crawling vs. MD-Only

**Updated:** 2026-05-12  
**Purpose:** Separate tracking of products by data acquisition method for v6_20.html and markdown generation

---

## List 1: CRAWLING LIST
### Products requiring full crawl + JSON extraction + MD generation

**Total:** 4 active + 58 complete = 62 products

### ⏳ In Progress / Pending (4 products)
| Model | Code | Category | Status | Scripts Ready | Notes |
|-------|------|----------|--------|----------------|-------|
| **SC9S** | SC95 (v6_20 오타) | Speaker | Pending data integration | ✓ finalize_sc9s.py | Gallery: 7, Features: 6 |
| **SH5A** | SHSA (v6_20 오타) | Speaker | Pending data integration | ✓ finalize_sh5a.py | Gallery: 11, Features: 4 |
| **RNC5** | RNC5 | Speaker | Pending data integration | ✓ finalize_rnc5.py | Gallery: 10, Features: 6 |
| **RNC7** | RNC7 | Speaker | ✓ Complete (crawled 2026-05-xx) | ✓ generate_markdown.py | Gallery: 20, Features: 22, Specs: 10 |

### ✓ Complete (58 products)
**All data crawled, extracted to JSON, integrated into v6_20.html, MD generated (some auto-generated, require manual review)**

| Category | Count | Sample Products |
|----------|-------|-----------------|
| TV/Monitor | 18 | 86QNED82A6A, 65QNED91A6A, 32GS95UV-B, 27US550-W, 27GX790A-B, 32SR50F-W, 32U721SA-W, etc. |
| Washer | 9 | WF2111BST, WK1310BST, WFV1214BST1, WTR22HHP, WS2112BST, WFN1510WHT, WFN1310BST, WFN1310WHT, WF0712MB |
| Refrigerator | 6 | RH10V9PV2W, RH18U8JVCW, RH81T2SP7RM, LS19GBBDI, LS25CBBDIK, LS19CBBSIN |
| Audio/Speaker | 7 | BUDS-BK, S90TR, S80TR, S45TR, S95TR, A9K-SOLO, A9LSLIM |
| Other (Monitor, Soundbar, Portable) | 12 | LT19CBBSIN, WTV17HHD, WTV11BND, WTV24HHP, LSEL6333D, DFC435FW, WTT1108OW1, WTT1410OL1, WSV0906XM, WFR1114WH, WFR1114MB, BOUNCE, GRAB, STAGE301, XG2TBK, XL2S |

**Workflow for Crawling List:**
1. Crawl PDP → Extract gallery images, features, specs
2. Save to `{PRODUCTCODE}_data.json`
3. Integrate to v6_20.html using `integrate_{PRODUCTCODE}.py` script
4. Generate initial markdown: `generate_markdown.py {PRODUCTCODE}_data.json {CATEGORY}`
5. Manual review: Enhance Key Features to "Feature: Benefit" format per geo_markdown_guide.md
6. Final markdown: `{model-code-lowercase}-product-info.md` ready for LLM indexing

---

## List 2: MD-ONLY LIST
### Products requiring only markdown creation (no crawling)

**Total:** 1 complete + 88 pending = 89 products

### ✓ Complete (1 product)
| Model | Code | Category | Market | MD File | Status | Analysis |
|-------|------|----------|--------|---------|--------|----------|
| **OLED evo AI TV 65-inch C5 2025** | OLED65C5PUA | TV | Canada | ✓ oled65c5pua-product-info.md | Complete | ✓ OLED65C5PUA-MD-ANALYSIS.md (7 sections: checklist, source attribution, spec completeness, LLM citation optimization, gaps, customization impact, tracking metadata) |

**Workflow for MD-Only List:**
1. Extract PDP content via Chrome/browser (manual or WebFetch)
2. Structure content per geo_markdown_guide.md sections
3. Create `{model-code-lowercase}-product-info.md` following template
4. Create analysis document: `{MODEL}-MD-ANALYSIS.md` showing:
   - Gap analysis vs. guide checklist
   - Source attribution (original PDP vs. customization)
   - Specification completeness
   - LLM citation optimization
5. No v6_20.html integration needed (products managed separately)

### ⏳ In Progress / Pending (88 products)

**LG Canada Market — All Categories**

#### TV / OLED (29 products)
| Model | Code | Market | Status |
|-------|------|--------|--------|
| OLED 42-inch C5 | OLED42C5PUA | Canada | ⏳ Pending MD |
| OLED 48-inch B5 | OLED48B5PUA | Canada | ⏳ Pending MD |
| OLED 48-inch C5 | OLED48C5PUA | Canada | ⏳ Pending MD |
| OLED 55-inch B5 | OLED55B5PUA | Canada | ⏳ Pending MD |
| OLED 55-inch C5 | OLED55C5PUA | Canada | ⏳ Pending MD |
| OLED 55-inch G5 (SUB) | OLED55G5SUB | Canada | ⏳ Pending MD |
| OLED 55-inch G5 (WUA) | OLED55G5WUA | Canada | ⏳ Pending MD |
| OLED 55-inch G6 (SUB) | OLED55G6SUB | Canada | ⏳ Pending MD |
| OLED 65-inch B5 | OLED65B5PUA | Canada | ⏳ Pending MD |
| OLED 65-inch C5 YUA | OLED65C5YUA | Canada | ⏳ Pending MD |
| OLED 65-inch C6 | OLED65C6PUA | Canada | ⏳ Pending MD |
| OLED 65-inch G5 (SUB) | OLED65G5SUB | Canada | ⏳ Pending MD |
| OLED 65-inch G5 (WUA) | OLED65G5WUA | Canada | ⏳ Pending MD |
| OLED 65-inch G6 (SUB) | OLED65G6SUB | Canada | ⏳ Pending MD |
| OLED 65-inch G6 (WUA) | OLED65G6WUA | Canada | ⏳ Pending MD |
| OLED 77-inch B5 | OLED77B5PUA | Canada | ⏳ Pending MD |
| OLED 77-inch C5 | OLED77C5PUA | Canada | ⏳ Pending MD |
| OLED 77-inch C5 YUA | OLED77C5YUA | Canada | ⏳ Pending MD |
| OLED 77-inch C6 HUP | OLED77C6HUP | Canada | ⏳ Pending MD |
| OLED 77-inch G5 | OLED77G5WUA | Canada | ⏳ Pending MD |
| OLED 77-inch G6 P | OLED77G6P | Canada | ⏳ Pending MD |
| OLED 77-inch G6 | OLED77G6WUA | Canada | ⏳ Pending MD |
| OLED 77-inch T4 | OLED77T4PUA | Canada | ⏳ Pending MD |
| OLED 83-inch B5 | OLED83B5PUA | Canada | ⏳ Pending MD |
| OLED 83-inch C5 | OLED83C5PUA | Canada | ⏳ Pending MD |
| OLED 83-inch C6 HUP | OLED83C6HUP | Canada | ⏳ Pending MD |
| OLED 83-inch G5 | OLED83G5WUA | Canada | ⏳ Pending MD |
| OLED 83-inch G6 | OLED83G6WUA | Canada | ⏳ Pending MD |
| OLED 97-inch G5 | OLED97G5WUA | Canada | ⏳ Pending MD |

#### Refrigerators (29 products)
| Model | Code | Type | Market | Status |
|-------|------|------|--------|--------|
| LG French Door Refrigerator | LF20C6330S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LF21C6200S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LF24C8200S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LF24Z6530S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LF25H6200S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LF25H6330S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LF25S6200S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LF25S6330S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LF25S6560S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LF25Z6211S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LF29S8365S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LF30S8210S | French-Door | Canada | ⏳ Pending MD |
| LG Bottom Freezer Refrigerator | LBNC12231V | Bottom-Freezer | Canada | ⏳ Pending MD |
| LG Bottom Freezer Refrigerator | LBNC15251V | Bottom-Freezer | Canada | ⏳ Pending MD |
| LG Bottom Freezer Refrigerator | LRDNS2200S | Bottom-Freezer | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LRFLC2706S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LRFLS3206S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LRFNS2200S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LRFS28XBS | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LRFWS2200S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LRFXC2606S | French-Door | Canada | ⏳ Pending MD |
| LG One-Door Refrigerator | LROFC1104V | One-Door | Canada | ⏳ Pending MD |
| LG One-Door Refrigerator | LRONC1404V | One-Door | Canada | ⏳ Pending MD |
| LG Kimchi Specialty Refrigerator | LK12S6000V | Kimchi | Canada | ⏳ Pending MD |
| LG Kimchi Refrigerator | LK14S8000V | Kimchi | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LRYXC2606S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator | LRYXS3106S | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator (Stainless) | SRFB27S3 | French-Door | Canada | ⏳ Pending MD |
| LG French Door Refrigerator (White) | SRFB27W3 | French-Door | Canada | ⏳ Pending MD |

#### Laundry / Washers (30 products)
| Model | Code | Type | Market | Status |
|-------|------|------|--------|--------|
| LG Washer-Dryer Combo | WM6998HBA | Combo | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM3400CW | Washer | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM6700HBA | Washer | Canada | ⏳ Pending MD |
| LG Washer-Dryer Combo | WM3555HVA | Combo | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM3600HWA | Washer | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM3850HVA | Washer | Canada | ⏳ Pending MD |
| LG Washer-Dryer Combo | WKE100HWA | Combo | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM6500HBA | Washer | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM8900HBA | Washer | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM3470CW | Washer | Canada | ⏳ Pending MD |
| LG Top Load Washer | WT8600CB | Top-Load | Canada | ⏳ Pending MD |
| LG Top Load Washer | WT8200CW | Top-Load | Canada | ⏳ Pending MD |
| LG Top Load Washer | WD6700-B | Top-Load | Canada | ⏳ Pending MD |
| LG Top Load Washer | WT6105CW | Top-Load | Canada | ⏳ Pending MD |
| LG Top Load Washer | WT8205CW | Top-Load | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM1455HWA | Washer | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM4100HWA | Washer | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM5500HVA | Washer | Canada | ⏳ Pending MD |
| LG Top Load Washer | WT8405CW | Top-Load | Canada | ⏳ Pending MD |
| LG Top Load Washer | WT8400CW | Top-Load | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM3580CX | Washer | Canada | ⏳ Pending MD |
| LG Top Load Washer | WT8405CB | Top-Load | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM3600HVA | Washer | Canada | ⏳ Pending MD |
| LG Washer-Dryer Combo | WKEX200HWA | Combo | Canada | ⏳ Pending MD |
| LG Top Load Washer | WT7010CW | Top-Load | Canada | ⏳ Pending MD |
| LG Washer-Dryer Combo | WKGX201HBA | Combo | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM5800HVA | Washer | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM4100HBA | Washer | Canada | ⏳ Pending MD |
| LG Top Load Washer | WT8400CB | Top-Load | Canada | ⏳ Pending MD |
| LG Front Load Washer | WM3400CV | Washer | Canada | ⏳ Pending MD |

---

## Comparison Matrix: Crawling List vs. MD-Only List

| Aspect | Crawling List | MD-Only List |
|--------|---------------|------------|
| **Data Source** | Live PDP crawl (gallery images, feature carousels, specs) | Manual extraction from PDP text/HTML or external sources |
| **Extraction Method** | Python scripts (regex, JSON-LD parsing, image header analysis) | Browser/WebFetch, manual copy-paste, structured reading |
| **Image Handling** | Auto-download gallery images to CDN folder, dimension detection | Not applicable (MD-only, no image integration to v6_20.html) |
| **v6_20.html Integration** | ✓ Yes — product entry added to const P = [...] array | ✗ No — separate tracking, not in HTML product database |
| **Interactive Detail Panel** | ✓ Yes — showDetail() function displays images + specs | ✗ No — product only exists as static .md file |
| **Markdown Generation** | Auto-generated (requires manual "Feature: Benefit" enhancement) | Hand-crafted per guide (includes full compliance checks) |
| **Analysis Documentation** | None (assumed complete after integration) | ✓ Detailed analysis markdown showing gaps, sources, LLM optimization |
| **Reusability** | Scripts can be templated for similar products | Template structure reusable, but customization per product |
| **Ideal Use Case** | Products needing v6_20.html product catalog display + LLM-optimized MD | Products with rich existing PDP content, no image gallery needed, or external sources |
| **Example Products** | RNC7 (crawled from LG Saudi Arabia PDP), SC9S, SH5A, 58 complete products | OLED65C5PUA (extracted from LG Canada PDP, markdown-only for now) |

---

## File Organization Summary

```
RetailOBS/3P/
├── generate_markdown.py                 ← Utility for auto-generating MD from JSON
├── integrate_rnc7.py                    ← Crawling List: RNC7 integration script
├── finalize_sc9s.py                     ← Crawling List: SC9S integration script
├── finalize_sh5a.py                     ← Crawling List: SH5A integration script
├── finalize_rnc5.py                     ← Crawling List: RNC5 integration script
│
├── LG_AI_Content_Hub_v6_20.html        ← Main product database (62 complete ✓)
│   └── const P = [                      ← Crawling List products (62 with full data)
│       {id:"SC9S", gal:7, feat:6, sp:22},
│       {id:"SH5A", gal:11, feat:4, sp:14},
│       {id:"RNC5", gal:10, feat:6, sp:17},
│       {id:"RNC7", gal:20, feat:22, sp:10},
│       ... (58 more)
│       ]
│
├── CRAWLING-LIST/
│   ├── rnc7_data.json                   ← RNC7 intermediate JSON (crawl output)
│   ├── rnc7-product-info.md             ← RNC7 auto-generated MD (requires review)
│   ├── sc9s_data.json
│   ├── sc9s-product-info.md
│   ├── [etc. for pending products]
│   └── COMPLETE/ (58 products with full data)
│       └── [models with gal+feat complete]
│
├── MD-ONLY-LIST/
│   ├── oled65c5pua-product-info.md      ← MD-Only: Hand-crafted MD
│   ├── OLED65C5PUA-MD-ANALYSIS.md       ← MD-Only: Analysis document
│   └── [future products...]
│
└── PRODUCT-MANAGEMENT-LISTS.md          ← This file (tracking both lists)
```

---

## Data Flow Diagram

### Crawling List Flow:
```
PDP URL
   ↓
crawl_PRODUCTCODE.py
   ↓
{PRODUCTCODE}_data.json
   ↓
integrate_PRODUCTCODE.py
   ↓
LG_AI_Content_Hub_v6_20.html (updated)
   ↓
generate_markdown.py {PRODUCTCODE}_data.json
   ↓
{model-code}-product-info.md (auto-generated, needs review)
   ↓
Manual enhancement: "Feature: Benefit" format per guide
   ↓
Final: {model-code}-product-info.md (LLM-optimized)
```

### MD-Only List Flow:
```
PDP URL
   ↓
Chrome browser / WebFetch / Manual extraction
   ↓
Structure content per geo_markdown_guide.md
   ↓
{model-code}-product-info.md (hand-crafted)
   ↓
Create {MODEL}-MD-ANALYSIS.md
   ├─ Gap analysis vs. guide
   ├─ Source attribution
   ├─ Spec completeness
   ├─ LLM citation optimization
   └─ Compliance verification
   ↓
Final: Both files ready for LLM indexing
```

---

## Key Decisions & Rationale

### Why Two Separate Lists?

1. **Different Workflows:** Crawling requires image management + v6_20.html integration; MD-only focuses on content structure per guide
2. **User Intent:** Some products (like OLED65C5PUA) prioritize LLM citation over HTML catalog display
3. **Scalability:** Separating lists allows independent scaling of each workflow
4. **Analysis Depth:** MD-only products get comprehensive gap/source analysis; crawling list gets integration scripts

### When to Use Crawling List:
- PDP has rich gallery images worth extracting
- Product needs v6_20.html interactive detail panel display
- Organization wants to populate product database at scale (consistent JSON structure)

### When to Use MD-Only List:
- Content already well-documented in existing PDP
- Focus is LLM citation optimization over HTML interactivity
- Product sourced from non-standard sources (press releases, spec sheets, external documentation)
- Rapid MD creation needed without Python script development

---

## Status Dashboard (2026-05-12 Updated)

| List | Total | Complete | Pending | Active | Completion % |
|------|-------|----------|---------|--------|--------------|
| **Crawling List** | 62 | **62** | 0 | ✅ All Complete | **100%** |
| **MD-Only List** | 89 | 1 | 88 | OLED65C5PUA + 88 Canada products | **1%** |
| **TOTAL** | **151** | **63** | **88** | — | **42%** |

### Crawling List ✅ COMPLETE
- SC9S: 7 gallery, 6 features, 22 specs ✓
- SH5A: 11 gallery, 4 features, 14 specs ✓
- RNC5: 10 gallery, 6 features, 17 specs ✓
- RNC7: 20 gallery, 22 features, 10 specs ✓
- 58 existing products: All integrated into v6_20.html ✓

### Next Actions:
- [ ] **MD-Only List Processing** (88 Canada products):
  - Phase 1: Process first 10-15 high-priority products (OLED C5/G5 sizes, key refrigerators)
  - Phase 2: WebFetch PDP → Extract content → Generate markdown per geo_markdown_guide.md
  - Phase 3: Create analysis documents for citation optimization
- [ ] Implement batch processing workflow for 88 pending products
- [ ] Consider auto-generation pipeline for repeated product variants
- [ ] Create MD-ONLY-LIST/ folder structure for organized storage
