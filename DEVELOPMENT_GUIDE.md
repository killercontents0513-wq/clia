# LG_AI_Content_Hub v6.20 — Development Guide

**Last Updated:** 2026-05-08  
**Status:** v6_20.html is the production file. All Python scripts are for data management and integration.

---

## 📋 File Structure

```
LG_AI_Content_Hub_v6_20.html       ← Main production file (67 products, ~2MB)
├── Crawl Data Scripts (26 files)
│   ├── crawl_*.py                 Extract product data from LG.com HTML
│   ├── crawl_*.html               Raw HTML from LG.com pages
│   └── Example: crawl_32u721sa.py
├── Integration Scripts (41 files)
│   ├── finalize_*.py              Complete product with gallery/features/specs
│   ├── integrate_*.py             Merge crawled data into v6_20.html
│   ├── build_*.py                 Build from scratch
│   └── Example: finalize_sc9s.py
├── Utility Scripts (4 files)
│   ├── extract_*.py               Extract specific fields
│   ├── verify_*.py                Validate data
│   └── Example: extract_feat_texts.py
└── Backup Versions (51 files)
    ├── v6_18.html, v6_17.html     Previous versions
    └── LG_AI_Content_Hub_v6_20.pre_*.html  Snapshots before edits
```

---

## 🔄 Workflow: Adding/Updating Products

### Step 1: Crawl LG.com
```bash
python3 crawl_[MODELCODE].py
```
**Output:** `crawl_[MODELCODE].html` (raw LG.com page)

### Step 2: Extract Data
```bash
python3 crawl_[MODELCODE]_v2.py  # or finalize_[MODELCODE].py
```
**Generates:**
- Gallery paths (large01.jpg, etc.)
- Feature data (title, description, image)
- Specifications
- Dimensions (via HTTP HEAD requests to CDN)

### Step 3: Inject into v6_20.html
```bash
python3 finalize_[MODELCODE].py
```
**Updates v6_20.html:**
- Replaces product entry
- Reorders product list (TOP_ORDER)
- Validates results

---

## 📊 Current Product Status (68 total)

### ✅ Complete (57 products)
Gallery + Features + Specs fully populated.  
Example: BUDS-BK (gal:15 feat:18), WFN1310BST (gal:15 feat:13)

### ⏳ Pending Finalization (11 products)
Scripts ready, awaiting execution:
- **SC95 → SC9S** (finalize_sc9s.py)
- **SHSA → SH5A** (finalize_sh5a.py)
- **RNC5** (finalize_rnc5.py)
- LT17CBBWIN, LS19CBBSIN, RH81T25P7RM, WFN130WHT, WRV1214BST1, WK2116BST1, MJ3965ACS, MJ3032JAS

### 🔧 Scripts Available for These
See `finalize_*.py` files in the root directory.

---

## 🛠️ Key Functions in v6_20.html

### Data Management
- `sel(id)` — Select product, show detail view
- `showDetail(p)` — Render product detail panel
- `renderList()` — Refresh product table
- `flt(f, el)` — Filter by category
- `sch(v)` — Search by text

### Content Generation
- `openCh(ch, pid)` — Generate content for channel (Amazon SA, eBay DE, Shopee, etc.)
- `openAplusBasicModal(pid)` — A+ Content registration form
- `openShortsGuide(pid)` — YouTube Shorts editing package
- `dlShortsPackage(pid)` — Download ZIP with scenes + narration + music brief

### Utility
- `I(path, size)` — Image URL transformer (CDN URL → sized variant)
- `findInHtml(id)` — Crawl modal to parse LG.com HTML
- `parseProductHtml(html)` — Extract gallery/features from crawled HTML

---

## 📝 Product Data Schema

Each product object contains:

```javascript
{
  id: "WFN1310BST",              // Model code
  dv: "HA",                       // Division (MS=Mobile, HA=Home)
  cat: "Washer",                  // Category
  sub: "Front Load",              // Subcategory
  ico: "🧺",                       // Emoji
  nm: "LG 13kg Front Load...",    // Full name
  pr: "SAR 3,949",                // Price SAR
  op: "SAR 6,599",                // Original price (if on sale)
  url: "https://www.lg.com/...",  // LG.com PDP link
  crawled: true,                  // Data completeness flag
  amz_title: "...",               // Amazon title
  amz_desc: "...",                // Amazon description
  
  // Gallery images
  gal: [
    {a: "Alt text", p: "/path/to/img.jpg", w: 1600, h: 1062},
    ...
  ],
  
  // Feature content
  feat: [
    {a: "Alt", p: "/path/img.jpg", t: "Title", d: "Description", w: 1600, h: 720},
    ...
  ],
  
  // Specifications
  sp: {
    "Type": "Front Load Washer",
    "Capacity": "13kg",
    ...
  },
  
  // Promotional callouts
  promo: [
    {icon: "Free Delivery", tip: "Free delivery across KSA"},
    ...
  ],
  
  // FAQ, keywords, bullets
  bul: ["Bullet 1...", "Bullet 2..."],
  faq: [{q: "Q?", a: "Answer"}, ...],
  kw: "space-separated keywords"
}
```

---

## 🚀 Next Steps

1. **Execute Pending Scripts** (if data updates needed):
   ```bash
   python3 finalize_sc9s.py
   python3 finalize_sh5a.py
   python3 finalize_rnc5.py
   ```

2. **Migrate to Claude Code** (for collaborative editing):
   - Move all files to a Claude Code project
   - Use `/loop` to batch-run finalize scripts
   - Test detail views in preview

3. **A+ Content Pipeline** (once all products complete):
   - Use `openCh('amzsa', 'MODEL')` to generate Amazon SA A+ HTML
   - Use `openAplusBasicModal(pid)` for registration forms
   - Export as ZIP with all assets

---

## 📞 Support

- **Detail button not showing?** → Check browser console for JS errors
- **Image CDN failures?** → Fallback to emoji icon (automatic)
- **Data incomplete?** → Run appropriate `finalize_*.py` script

---

## 🔐 Important Notes

- ✅ **v6_20.html** is the source of truth. All Python scripts modify it.
- ✅ **Backups** are auto-created before each major edit.
- ✅ **CDN URLs** are from `https://www.lg.com/content/dam/channel/wcms/sa_en/`
- ✅ **Browser-safe:** All JavaScript is client-side; no backend required.
