# CLIA Learning Log

Running notebook of per-product edits, tone patterns, and category rules discovered while building LG official English marketplace content.

## Benchmark / Golden Reference

**RH81T2SP7RM** — 8kg Heat Pump Dryer. Chosen as the golden reference because its PDP is sparse (1 feature module) so it forces the copy generator to derive content from specs alone. Any generator that makes RH81T2SP7RM look complete-and-premium will work for any product.

## LG Official English Tone — Style Guide

**Title pattern (Amazon-safe, ≤200 chars)**
`LG {capacity} {category-descriptor} with {top-3 selling features} — {design-or-color} ({model})`

Examples:
- `LG 8.0kg Heat Pump Dryer with Sensor Dry, Anti-Crease, Child Lock — Ventless Condenser Design (RH81T2SP7RM)`
- `LG 15kg Front Load Washing Machine with AI DD, Steam, TurboWash, ThinQ Wi-Fi — Official LG Saudi Arabia (WSN1508BMT)`

**Bullet pattern (≤500 chars, 5 bullets)**
- Each bullet opens with an ALL-CAPS short hook (3–5 words), em-dash, then one sentence of benefit language.
- Use LG's trademark terminology: `AI DD®`, `TurboWash™`, `TrueSteam™`, `LG ThinQ®`, `Smart Diagnosis™`, `Inverter DirectDrive`, `LINEAR Cooling™`, `AI Sound Pro`, `QuadWash™`, `webOS`.
- Always include one bullet about warranty / smart / energy efficiency.
- Avoid: "amazing", "incredible", raw superlatives without substance. LG tone is reserved and technical.

**Description pattern**
1. Opening: "Experience the {h1} ({model}) — engineered by LG to deliver best-in-class performance for modern homes in Saudi Arabia."
2. Bulleted feature list (same 5 bullets).
3. Closing: "Designed with LG's signature engineering, intuitive controls and trusted build quality. Backed by LG Electronics' official warranty and LG Saudi Arabia after-sales service network."

## Category → Copy Template Rules

| Category       | Capacity field                        | Must-have selling points                                     |
|---            |---                                    |---                                                           |
| Washer        | Max Wash Capacity(kg)                 | AI DD, Steam, TurboWash, ThinQ, Inverter DirectDrive         |
| Dryer         | Max Dry Capacity (kg)                 | Sensor Dry, Heat Source Type, Anti-Crease, Child Lock        |
| Refrigerator  | Storage Volume Total (L)              | LINEAR Cooling, Smart Inverter Compressor, Deodorizer        |
| TV            | Display Resolution                    | AI Picture Pro, Dolby Vision, Dolby Atmos, webOS, VRR        |
| Audio         | (none — use model tier)               | AI Sound Pro, Dolby Atmos, WOW Orchestra, LG ThinQ           |
| Vacuum        | Weight, Max Suction Power             | Run time, Smart Inverter Motor, 2-in-1 Convertibility        |
| Microwave     | Capacity (L)                          | Smart Inverter, EasyClean, Sensor Cooking                    |
| Dishwasher    | Total Place Settings                  | QuadWash, TrueSteam, Inverter Direct Drive                   |

## Per-Product Notes (to be filled as edits accumulate)

### 2026-04-20 — Initial batch
- **RH81T2SP7RM**: LG.com PDP is spec-only (1 feature block). Generator must handle specs-only PDPs.
- **WFN1310WHT, WFN1310BST, WFN1510WHT**: All share feature images from `wfn1510bst-aeggnag/` (LG reuses assets across siblings). Not a problem for hub usage, but Amazon A+ may want product-specific images.
- **TV (65QNED93A6A)**: Uses both `/images/tv/features/qned93/…` (legacy) and `/2025_ms_lg-com/tv/…` (new microsite) paths. Filter `/tv/` catches both.
- **Soundbars**:
  - `S95TR` → `/images/av/s95tr/…`
  - `S65TR` → `/images/audio-video/s65tr_asauelk/…` + `/images/av/s65tr/…` for features
  - `S20A` → `/speakers/soundbars/s20a/…`
  Three different path conventions for similar products. Use model slug in filter (e.g. `/s95tr/`, `/s65tr`, `/s20a/`).
- **WTR22HHP (Washer)**: Images stored under `/images/refrigerators/wtr22hhp/…` (LG data inconsistency). Use slug-based filter `/wtr22hhp/`.
- **MS3032JAS (Microwave)**: Category URL is `/cooking-appliances/microwaves/` but image path is `/images/microwaves/`.

## Resolution Policy

Crawler captures the **desktop** rendition of each image by reading `<picture> source[media~=min-width]`, then measuring via `new Image()` to get `naturalWidth × naturalHeight`. This preserves LG.com's actual desktop dimensions (1600×1062 for gallery, 1920×720 for hero banners, 340×340 for split-view features, 122×122 for icons).

## Gallery-Ordering Fix (discovered on LS25CBBDIK)

LG.com gallery uses **Swiper.js infinite loop**, which prepends a duplicate slide at DOM index 0. That duplicate is the LAST image in the intended order (e.g., the energy label or back view) being visually placed before slide 1 for loop continuity. As a result, a naive DOM-order crawl puts "back view" or "energy label" as the first product image — wrong for Amazon and every other channel.

**Fix**: exclude `.swiper-slide-duplicate` from the carousel item list. This yields the correct intended order: `dz-01 Front view → dz-02 → … → dz-13 energy label`.

```js
// Correct (LS25CBBDIK-fixed) gallery extraction
const items = [...document.querySelectorAll(
  '.c-gallery .cmp-carousel__item:not(.swiper-slide-duplicate) img'
)];
```

## Feature-Module Crawl Fix — Two Problems Discovered on LS25CBBDIK

**Problem 1 — Lazy-loaded images return empty `src`.** LG.com uses `class="lazyload"` on `<img>` and `<source>` elements. Until the element scrolls into view, `img.src` is empty and `source.srcset` is empty. The real URL lives in `data-src` (on `<img>`) and `data-srcset` (on `<source>`).

**Fix**: In `pickDesk()`, fall back to `dataset` attributes:
```js
const pickDesk = (img) => {
  const pic = img.closest('picture');
  if (pic) {
    const dSrc = [...pic.querySelectorAll('source')]
      .find(s => /min-width/.test(s.media || ''));
    if (dSrc) {
      const val = dSrc.srcset || dSrc.getAttribute('data-srcset') || '';
      if (val) return val.split(',')[0].trim().split(/\s+/)[0];
    }
  }
  return img.currentSrc || img.src || img.getAttribute('data-src') || '';
};
```

**Problem 2 — Scoping feature extraction by product-slug URL filter is wrong.** LG.com feature modules often use **generic lifestyle imagery** whose URL has no product slug (e.g., `/images/rf/REF-d.jpg`, `/images/rf/D01_LINEARCooling-D.jpg`). The previous crawler filtered images by `/ls25cbbdik/` and dropped every lifestyle asset, leaving only the SASO label and product-specific summary diagram.

**Fix**: Scope feature extraction to the PDP main content container `#pdp-overview-section`, then walk ALL `.c-hero-banner` and `.c-media-contents` blocks inside it. Do NOT filter by image URL; the scope already excludes nav, footer, cookie banners, and promo rails.

```js
const root = document.querySelector('#pdp-overview-section');
const blocks = [...root.querySelectorAll('.c-hero-banner, .c-media-contents')];
// Dedupe by (headline + first-image-path) to collapse repeated modules.
```

Result on LS25CBBDIK: 2 modules → **8 modules** (LinearCooling, Multi Air Flow, Large Capacity, UltraSleek Door, ThinQ Connect, Smart Alert, Smart Inverter Compressor, SASO label).

## Amazon A+ Image Fit — cover → contain (2026-04-20)

**Symptom on LS25CBBDIK**: Amazon A+ "Standard Image Header With Text" module rendered the LinearCooling image (1600×992) with visible cropping on the left/right — only the middle portion of the 3-photo collage was shown, cutting off the lettuce on the left edge and blueberries on the right edge.

**Root cause**: Both the preview CSS and the downloadable-PNG canvas generator used **cover-fill** semantics (`object-fit:cover` / `Math.max(W/srcW,H/srcH)`). With LG's wide lifestyle hero assets (often designed at ~3:2 or wider) placed in Amazon's 970×600 (~1.617:1) module, cover-fill crops the horizontal edges.

**Fix**: switched to **contain-fit** across all single-image A+ modules:
- CSS (`.apm-hero img`, `.apm-overlay img`, `.apm-split-img.sq img`): `object-fit: contain` + `aspect-ratio: 970/600` or `970/300` + white background.
- Canvas generators:
  - `drawAplusCanvas`: `Math.max` → `Math.min`
  - `drawModuleCanvas` (`header_with_text`): `Math.max` → `Math.min`
  - `drawCombinedCanvas` per-slot: flipped branch (fit-width when image is wider than slot).

**Trade-off**: When aspect ratios don't match, contain adds white letterbox bars. This is acceptable because:
1. LG lifestyle shots are intentionally composed (e.g., 3-photo collages) and should never be cropped.
2. Amazon A+ allows white-background images — it doesn't look out of place.
3. Users who want tight-crop can use a different module type (e.g., `img_dark_overlay` with text on top).

## Cross-Locale DAM Asset Reference (discovered on S95TR)

LG.com stores some images in the Saudi Arabic (`/content/dam/channel/wcms/sa/`) DAM and references them across locales (including from English `sa_en` pages). Our crawler correctly captures these as absolute URLs (`https://www.lg.com/content/dam/channel/wcms/sa/images/av/...`). BUT during curation if these are blindly stripped to relative paths (`/images/av/...`), the v6_18 `I()`/`imgUrl()` functions prepend `/sa_en/` — breaking the URL.

**Observed on S95TR module "HD Streaming"**:
- Raw URL: `https://www.lg.com/content/dam/channel/wcms/sa/images/av/av-soundbar-s95tr-11-hd-streaming-d-v2.jpg`
- Naive strip: `/images/av/av-soundbar-s95tr-11-hd-streaming-d-v2.jpg` → 404 under `/sa_en/`

**Fix** (2026-04-21):
1. Preserve absolute URLs during JSON curation (don't blindly strip to relative).
2. Patched `I()` and all 4 `imgUrl()` variants in v6_18 to pass-through absolute URLs:
   ```js
   if(/^https?:\/\//i.test(p)) return p;
   ```

Rule of thumb during curation: **if the raw crawl URL starts with `https://`, keep it verbatim**.

## Shared-Template Inconsistency (LG data quirk)

LG.com reuses feature modules across sibling models. On LS25CBBDIK the PDP shows:
- ✅ LinearCooling (spec: Yes)
- ✅ Smart Inverter Compressor (spec: Yes)
- ❌ Multi Air Flow (spec: **No**) — but module is shown anyway
- ❌ LG ThinQ Remote Control / Smart Alert (spec ThinQ Wi-Fi: **No**) — modules shown anyway
- ❌ UltraSleek Door image shows an InstaView model (spec InstaView: No)

**Implication for Amazon content**: When writing `bul` / `amz_title` / `amz_desc`, rely on the **spec table** as ground truth, not the feature modules. The feat array (in v6_18) faithfully reflects LG.com's PDP so multi-channel export is accurate, but marketing copy must only mention verified features.

## Per-Product Workflow (single-product mode)

As of 2026-04-20, switched from batch-of-30 to single-product-at-a-time because:
1. Batch crawler missed Swiper-duplicate ordering issue across all 30 products.
2. Batch-generated Amazon content was too generic.
3. Newest-first ordering needs to match the user's working queue.

**Per-product flow**:
1. Navigate to PDP and manually inspect gallery order / feature blocks.
2. Write a one-off JS extractor scoped to the product (includes `ls25cbbdik` slug filter, Swiper-duplicate exclusion).
3. Save per-product JSON to `crawl_v2/{ID}.json`.
4. Hand-craft `OVERRIDES[{ID}]` in `crawl_v2/_inject_single.py` with LG-tone Title / 5 Bullets / Description / Keywords.
5. Run `python crawl_v2/_inject_single.py {ID}` — replaces existing entry and pins to TOP of P[].

## Future Enhancements

- [ ] AI-polish pass: run each bullet through a second template pass to avoid verbatim repetition across products.
- [ ] Per-country tone overrides (e.g., UK/DE/FR localization keeping same rule engine).
- [ ] Spec-to-bullet mapping rules externalized to JSON for non-technical editing.
- [ ] Feature-image quality scoring so Amazon A+ module generator picks the best 5 images.
