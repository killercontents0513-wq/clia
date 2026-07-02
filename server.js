/**
 * CLIA Crawl Server — v1.4
 * LG.com PDP Crawler for eBay Listing Content Builder
 * Endpoints:
 *   GET  /api/health           — server health check
 *   POST /api/crawl-product    — crawl LG.com PDP → structured product data
 *
 * Gallery patterns supported (priority order, DZ preferred over D):
 *   /galleryN/DZ-NN.jpg          — Detail Zoom (highest quality, gallery\d*)
 *   /galleryN/D-NN.jpg           — Desktop (fallback when no DZ)
 *   /galleryN/...-NN.jpg         — Generic sequence filename
 *   N-WIDTH.jpg (no /gallery/ dir) — Dishwasher-style reversed numeric
 *   WIDTH-N.jpg (no /gallery/ dir) — Monitor-style numeric
 *   -gallery-WIDTH-N.jpg in name   — Washer flat-filename style
 *   /NNNxNNN/-add-N-NNN.jpg        — D2C / de format
 *
 * Feature patterns supported:
 *   -Desktop.jpg / -desktop-vari-NN.jpg
 *   -d.jpg / -D.jpg / _D.jpg (all case variants)
 *   D\d\d_...-D.jpg (dryer/HA prefixed desktop)
 *   /features/desktop/ directory
 *   -desktop-NN- in filename (XBoom/GRAB)
 */

'use strict';

const express = require('express');
const cors    = require('cors');
const axios   = require('axios');

const app  = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

const UA  = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36';
const CDN = 'https://www.lg.com/content/dam/channel/wcms/sa_en';
// locale-agnostic CDN base: matches /content/dam/channel/wcms/ANY_LOCALE/
const LC  = String.raw`\/content\/dam\/channel\/wcms\/[^\/\s"'\\]+\/`;

// ─── Health check ─────────────────────────────────────────────────
app.get('/api/health', (_req, res) => {
  res.json({ ok: true, ts: Date.now() });
});

// ─── Category from URL ─────────────────────────────────────────────
function catFromUrl(url) {
  const u = url.toLowerCase();
  if (/oled|qned|nanocell|tv-soundbar|\/tv\b/.test(u)) return 'TV';
  if (/soundbar/.test(u)) return 'Audio';
  if (/speaker|xboom|earbuds|wireless-earbuds|party-speaker/.test(u)) return 'Audio';
  if (/washing|washer|washtower/.test(u)) return 'Washer';
  if (/dryer/.test(u)) return 'Dryer';
  if (/refrigerator|fridge|freezer/.test(u)) return 'Fridge';
  if (/dishwasher/.test(u)) return 'Dishwasher';
  if (/monitor/.test(u)) return 'Monitor';
  if (/cooking|cooker|range|oven/.test(u)) return 'Cooking';
  if (/air.condition|air.purifier|hvac/.test(u)) return 'AC';
  return 'Other';
}

// ─── Gallery ──────────────────────────────────────────────────────
//
// LG gallery sub-types to skip (prefer DZ/D desktop over mobile/thumbnail variants):
//   MZ = Mobile Zoom, TH = Thumbnail, S = Swatch, Basic = basic shot
//   Also skip global noise: mobilezoom, thumbnail, banner, gnb, icons
// D-NN = Desktop lower-quality variant; skip in favour of DZ-NN (\/D-\d matches /D-01 but not /DZ-01)
const GAL_SKIP = /thumbnail|mobilezoom|basic-large|basic_large|-logo-|_logo[_\s]|_logo$|-kv-|award|gnb|banner|icon|\/MZ-\d|\/TH-\d|\/S-\d+\.|\/Basic\.|\/D-\d|\/DZ-\d+V\b|energy-star|minicard|contentcard|promo|angi[-_]logo|\/lg_a|credit|sling/i;

function extractGallery(html, nm, modelId) {
  const seen = new Set();
  const imgs = [];

  function addImg(key, num) {
    const clean = key.split('?')[0];
    if (GAL_SKIP.test(clean)) return;
    if (!seen.has(clean)) { seen.add(clean); imgs.push({ p: clean, num }); }
  }

  // ── Tier 0b: data-large-m attributes — DE/EU zoom gallery images (highest priority, highest res)
  {
    const zoomMap = new Map();
    for (const m of html.matchAll(/data-large-m="([^"]+)"/gi)) {
      const path = m[1].split('?')[0];
      if (GAL_SKIP.test(path)) continue;
      const seqM = path.match(/[_-](?:zoom|gallery)-(\d+)-with-logo/i) || path.match(/[_-](\d{2,3})-with-logo/i);
      const seq = seqM ? parseInt(seqM[1]) : zoomMap.size + 200;
      const full = /^https?:\/\//i.test(path) ? path : 'https://www.lg.com' + path;
      zoomMap.set(seq, { p: full, num: seq });
    }
    if (zoomMap.size > 0) {
      [...zoomMap.values()].sort((a, b) => a.num - b.num).forEach(v => addImg(v.p, v.num));
    }
  }

  // ── Tier 0: US media CDN (media.us.lg.com/transform/ecomm-PDPGallery-*)
  // Pattern: ecomm-PDPGallery-{size}/{uuid}/{filename}  — skip Thumbnail variant
  {
    const usMap = new Map();
    // Extract core model number from modelId (e.g. "LG-OLED77G6WUA-OLED-4K-TV" → "OLED77G6WUA")
    const coreModel = modelId ? (modelId.match(/([A-Z0-9]{6,15})/g) || []).find(s => /\d/.test(s) && s.length >= 6) : '';
    for (const m of html.matchAll(/https?:\/\/media\.us\.lg\.com\/transform\/ecomm-PDPGallery(?!Thumbnail)-[^/"'\s\\]+\/([a-f0-9-]{36})\/([^"'\s?\\]+)/gi)) {
      const clean = m[0].split('?')[0];
      if (GAL_SKIP.test(clean)) continue;
      // infographic or features images → routed to feat (extracted separately)
      if (/infographic|_features_|features_\d/i.test(m[2])) continue;
      // If another model number appears in filename but NOT our model, skip
      if (coreModel && /[A-Z]{2,5}\d{2,3}[A-Z0-9]{4,}/i.test(m[2]) && !m[2].toUpperCase().includes(coreModel)) continue;
      const numM = m[2].match(/(?<![a-z])gallery[-_]?0*(\d+)/i);
      const seq  = numM ? parseInt(numM[1]) : (usMap.size + 100);
      if (!usMap.has(seq) || usMap.get(seq).p.length < clean.length) usMap.set(seq, { p: clean, num: seq });
    }
    if (usMap.size > 0) {
      [...usMap.values()].sort((a, b) => a.num - b.num).forEach(v => addImg(v.p, v.num));
    }
  }

  // ── Tier 1: DZ (Detail Zoom) — highest quality, gallery\d* covers gallery, gallery1, gallery2 …
  // Relative path (old SA CDN prefix style)
  for (const m of html.matchAll(/\/images\/[^"'\s?\\]+\/gallery\d*\/DZ-(\d+)\.jpg/gi)) {
    addImg(CDN + m[0], parseInt(m[1]));
  }
  // Absolute /content/dam/… path (any locale)
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/gallery\d*\/DZ-(\d+)\.jpg`, 'gi'))) {
    addImg('https://www.lg.com' + m[0], parseInt(m[1]));
  }

  // ── Tier 1b: D-NN (Desktop, lower quality than DZ but better than MZ)
  // Only added when no DZ found (checked after sort/dedupe below)
  const dImgs = [];
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/gallery\d*\/D-(\d+)\.jpg`, 'gi'))) {
    const clean = ('https://www.lg.com' + m[0]).split('?')[0];
    if (!GAL_SKIP.test(clean)) dImgs.push({ p: clean, num: parseInt(m[1]) });
  }

  // ── Tier 2: generic gallery/...-NN.jpg (sequence ≤ 99)
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/gallery\d*\/[^"'\s?\\]+-(\d{1,2})\.jpg`, 'gi'))) {
    addImg('https://www.lg.com' + m[0].split('?')[0], parseInt(m[1]));
  }
  // absolute https:// variant
  for (const m of html.matchAll(/https:\/\/www\.lg\.com\/content\/dam\/channel\/wcms\/[^"'\s?\\]+\/gallery\d*\/[^"'\s?\\]+-(\d{1,2})\.jpg/gi)) {
    addImg(m[0].split('?')[0], parseInt(m[1]));
  }

  // ── Tier 2c: DE/EU locale gallery/large{NN}.jpg format (prefer large over small)
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/gallery\/large(\d+)\.jpg`, 'gi'))) {
    if (/small/i.test(m[0])) continue;
    addImg('https://www.lg.com' + m[0].split('?')[0], parseInt(m[1]));
  }

  // ── Tier 2b: JCR rendition paths
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/gallery\d*\/[^"'\s?\\]+\.jpg(?=\/jcr:content\/renditions\/)`, 'gi'))) {
    const numM = m[0].match(/-(\d{1,2})-?\d*\.jpg$/i);
    addImg('https://www.lg.com' + m[0], numM ? parseInt(numM[1]) : seen.size);
  }

  // ── Tier 3: Flat -gallery-NN.jpg in filename (no /gallery/ subdir)
  for (const m of html.matchAll(new RegExp(LC + String.raw`images\/[^"'\s?\\]+-gallery-(\d+)\.jpg`, 'gi'))) {
    addImg('https://www.lg.com' + m[0].split('?')[0], parseInt(m[1]));
  }

  // ── Tier 3b: Flat filename -gallery-WIDTH-SEQ.jpg (washer-style, no /gallery/ subdir)
  //   e.g. top-loading-washing-machine-tx-2024-gallery-gallery-2010-01.jpg
  if (imgs.length === 0) {
    const flatMap = new Map();
    for (const m of html.matchAll(new RegExp(LC + String.raw`images\/[^"'\s?\\]*-?gallery-(\d{3,4})-(\d{1,2})\.jpg`, 'gi'))) {
      if (GAL_SKIP.test(m[0])) continue;
      const width = parseInt(m[1]), seq = parseInt(m[2]);
      const key = 'https://www.lg.com' + m[0].split('?')[0];
      if (!flatMap.has(seq) || flatMap.get(seq).width < width) flatMap.set(seq, { width, path: key });
    }
    if (flatMap.size > 0) {
      [...flatMap.entries()].sort((a, b) => a[0] - b[0]).forEach(([seq, v]) => addImg(v.path, seq));
    }
  }

  // ── Tier 4: D2C / de format: gallery/NNNxNNN/...-add-N-NNN.jpg
  if (imgs.length === 0) {
    const d2cMap = new Map();
    for (const m of html.matchAll(/\/content\/dam\/channel\/wcms\/[^"'\s?\\]+\/gallery\/(\d+)x\d+\/[^"'\s?\\]+-add-(\d+)-(\d+)\.jpg/gi)) {
      const res = parseInt(m[1]), seq = parseInt(m[2]);
      const key = 'https://www.lg.com' + m[0].split('?')[0];
      if (!d2cMap.has(seq) || d2cMap.get(seq).res < res) d2cMap.set(seq, { res, path: key });
    }
    [...d2cMap.entries()].sort((a, b) => a[0] - b[0]).forEach(([seq, v]) => addImg(v.path, seq));
  }

  // ── Tier 5: WIDTH-N.jpg numeric (e.g. 2010-1.jpg) — Monitor/TV style, pick highest width
  if (imgs.length === 0) {
    const wMap = new Map();
    for (const m of html.matchAll(new RegExp(LC + String.raw`images\/[^"'\s?\\]+\/(\d{3,4})-(\d{1,2})\.jpg`, 'gi'))) {
      const width = parseInt(m[1]), seq = parseInt(m[2]);
      if (width < 500) continue; // skip small portrait/square images (350px etc.)
      const key = 'https://www.lg.com' + m[0].split('?')[0];
      if (!wMap.has(seq) || wMap.get(seq).width < width) wMap.set(seq, { width, path: key });
    }
    if (wMap.size > 0) {
      [...wMap.entries()].sort((a, b) => a[0] - b[0]).forEach(([seq, v]) => addImg(v.path, seq));
    }
  }

  // ── Tier 5b: N-WIDTH.jpg numeric (e.g. 1-2010.jpg) — Dishwasher reversed style
  if (imgs.length === 0) {
    const rMap = new Map();
    for (const m of html.matchAll(new RegExp(LC + String.raw`images\/[^"'\s?\\]+\/(\d{1,2})-(\d{3,4})\.jpg`, 'gi'))) {
      const seq = parseInt(m[1]), width = parseInt(m[2]);
      const key = 'https://www.lg.com' + m[0].split('?')[0];
      if (!rMap.has(seq) || rMap.get(seq).width < width) rMap.set(seq, { width, path: key });
    }
    if (rMap.size > 0) {
      [...rMap.entries()].sort((a, b) => a[0] - b[0]).forEach(([seq, v]) => addImg(v.path, seq));
    }
  }

  // ── Tier 6: MZ fallback (mobile zoom — only when nothing else found)
  if (imgs.length === 0) {
    for (const m of html.matchAll(new RegExp(LC + String.raw`images\/[^"'\s?\\]+\/MZ-(\d+)\.jpg`, 'gi'))) {
      addImg('https://www.lg.com' + m[0].split('?')[0], parseInt(m[1]));
    }
  }

  // ── Tier 7: final fallback — any /gallery\d*/ path
  if (imgs.length === 0) {
    for (const m of html.matchAll(/\/content\/dam\/channel\/wcms\/[^"'\s?\\]+\/gallery\d*\/[^"'\s?\\]+\.jpg/gi)) {
      if (GAL_SKIP.test(m[0])) continue;
      addImg('https://www.lg.com' + m[0].split('?')[0], seen.size);
      if (imgs.length >= 12) break;
    }
  }

  // Merge D-type images if DZ produced nothing
  if (imgs.length === 0 && dImgs.length > 0) {
    dImgs.sort((a, b) => a.num - b.num);
    dImgs.forEach(d => { if (!seen.has(d.p)) { seen.add(d.p); imgs.push(d); } });
  }

  imgs.sort((a, b) => a.num - b.num);

  // Dedup by sequence: if same num, keep the highest-res image (largest dimension number in path)
  {
    const numMap = new Map();
    for (const img of imgs) {
      const dims = [...img.p.matchAll(/(\d{3,4})x(\d{3,4})/g)].map(m => parseInt(m[1]));
      const res = dims.length ? Math.max(...dims) : (img.p.includes('/large') ? 800 : 600);
      if (!numMap.has(img.num) || res > numMap.get(img.num).res) numMap.set(img.num, { img, res });
    }
    imgs.splice(0, imgs.length, ...[...numMap.values()].sort((a, b) => a.img.num - b.img.num).map(v => v.img));
  }

  // Back/rear images must NOT be first
  const BACK_PAT = /-back[-_]|-rear[-_]|_back\.|_rear\.|[-_]back\.jpg$|[-_]rear\.jpg$/i;
  const top20    = imgs.slice(0, 20);
  console.log('[GAL DEBUG]', nm, top20.map(i => i.p.split('/').slice(-1)[0]));
  const nonBack  = top20.filter(i => !BACK_PAT.test(i.p));
  const backImgs = top20.filter(i =>  BACK_PAT.test(i.p));

  return [...nonBack, ...backImgs].map(({ p }, i) => ({ a: `${nm} — View ${i+1}`, p, w: 1600, h: 1062 }));
}

// ─── Features ─────────────────────────────────────────────────────
//
// Desktop image detection rules (case-insensitive throughout):
//   1. -Desktop.jpg (explicit Desktop suffix)
//   2. /features/desktop/ directory
//   3. -d.jpg / -D.jpg / _D.jpg / _d.jpg (single-letter desktop suffix)
//   4. D\d\d_...-D.jpg (HA prefix style: D01_name-D.jpg)
//   5. -desktop-vari-NN.jpg (fridge new-style)
//   6. -desktop-NN- in filename (XBoom/GRAB)
//   7. /feature/desktop/ directory (GRAB variant)
//   8. Flat -feature-NN-...-d.jpg
function extractFeatures(html, modelId, locale) {
  const seen    = new Set(); // dedup by URL
  const seenFn  = new Set(); // dedup by filename — prevents cross-locale duplicates
  const raw     = [];

  // Skip: intro KV/logo/badge noise, mobile variants (-M.jpg / _M.jpg / -mobile- / -m_v.jpg / -m123.jpg), icons, thumbnails
  const FEAT_SKIP = /feature-00|feature-\d+-\d+-\d+-\d+|-gnb-|-banner-|-icon-|-thumbnail|-mobile[-_]|[-_]mobile[-_]|[-_]mobile\.jpg$|icon\.(?:png|jpg)$|[-_][Mm]\.jpg$|[-_][Mm]_[Vv]\.jpg$|[-_][Mm]\d+\.jpg$|[-_][Mm][-_]\d|[-_][Mm][-_][Vv]|[-_][Mm]\d+[-_]/i;

  // Locale prefix for prioritization (e.g. '/wcms/de/' when crawling lg.com/de/)
  const localePfx = locale ? `/wcms/${locale}/` : '';

  function addFeat(key) {
    const clean = key.split('?')[0];
    if (FEAT_SKIP.test(clean)) return;
    const fn = clean.split('/').pop();
    // Prefer locale-matching path: if we already have this filename from a different locale, replace if current locale matches
    if (seenFn.has(fn)) {
      if (localePfx && clean.includes(localePfx)) {
        // Replace existing non-locale entry with locale-specific one
        const idx = raw.findIndex(r => r.split('/').pop() === fn && !r.includes(localePfx));
        if (idx >= 0) { seen.delete(raw[idx]); raw.splice(idx, 1, clean); seen.add(clean); }
      }
      return;
    }
    if (!seen.has(clean)) { seen.add(clean); seenFn.add(fn); raw.push(clean); }
  }

  function featType(path) {
    const f = path.toLowerCase();
    if (/-logo-/.test(f))    return 'logo';
    if (/-kv-/.test(f))      return 'kv';
    if (/-summary-/.test(f)) return 'summary';
    if (/-award-|-certification-|-warranty-/.test(f)) return 'badge';
    return 'feature';
  }

  // 0. US media CDN — infographic_gallery and _features_ images treated as feature/PDP images
  //    e.g. ecomm-PDPGallery-1100x730/{uuid}/TVs_OLED77G6WUA_infographic_gallery-04_3000x3000
  //         ecomm-PDPGallery-1100x730/{uuid}/TV-OLED77G6WUA-Hyper-Radiant-features_900x600
  {
    const usInfoMap = new Map();
    // Extract core model number for filtering out other-size variants
    // Prefer modelId passed from crawl (e.g. "LG-OLED77G6WUA-OLED-4K-TV" → "OLED77G6WUA")
    const usInfoModelRaw = (() => {
      if (modelId) {
        const parts = modelId.toUpperCase().match(/([A-Z0-9]{5,15})/g) || [];
        const m = parts.find(s => /\d/.test(s) && s.length >= 6);
        if (m) return m;
      }
      return '';
    })();
    for (const m of html.matchAll(/https?:\/\/media\.us\.lg\.com\/transform\/ecomm-PDPGallery(?!Thumbnail)-[^/"'\s\\]+\/([a-f0-9-]{36})\/([^"'\s?\\]+)/gi)) {
      const fn = m[2];
      if (!/infographic|_features_|features_\d/i.test(fn)) continue;
      const clean = m[0].split('?')[0];
      if (FEAT_SKIP.test(clean)) continue;
      // Skip other model variants (e.g. OLED65G6WUA, OLED83G6WUA)
      if (usInfoModelRaw && /[A-Z]{2,5}\d{2,3}[A-Z0-9]{4,}/i.test(fn) && !fn.toUpperCase().includes(usInfoModelRaw)) continue;
      const numM = fn.match(/gallery[-_]?0*(\d+)/i) || fn.match(/features_(\d+)/i);
      const seq  = numM ? parseInt(numM[1]) : (usInfoMap.size + 100);
      if (!usInfoMap.has(seq)) usInfoMap.set(seq, { p: clean, seq });
    }
    if (usInfoMap.size > 0) {
      [...usInfoMap.values()].sort((a, b) => a.seq - b.seq).forEach(v => {
        if (!seen.has(v.p)) { seen.add(v.p); raw.push(v.p); }
      });
    }
  }

  // 0b. US media CDN explicit feature transform types (ecomm-PDPFeature-* / ecomm-PDPDetail-*)
  for (const m of html.matchAll(/https?:\/\/media\.us\.lg\.com\/transform\/ecomm-PDP(?:Feature|Detail|Section)-[^/"'\s\\]+\/[a-f0-9-]{36}\/([^"'\s?\\]+)/gi)) {
    const clean = m[0].split('?')[0];
    if (FEAT_SKIP.test(clean)) continue;
    addFeat(clean);
  }

  // 1. -Desktop.jpg (case-insensitive) — old SA CDN relative path
  for (const m of html.matchAll(/\/images\/[^"'\s?\\]+\/features\/[^"'\s?\\]+-Desktop\.jpg/gi)) {
    if (/thumbnail/i.test(m[0])) continue;
    addFeat(CDN + m[0]);
  }
  // 1b. any locale absolute
  for (const m of html.matchAll(new RegExp(LC + String.raw`images\/[^"'\s?\\]+\/features\/[^"'\s?\\]+-Desktop\.jpg`, 'gi'))) {
    if (/thumbnail/i.test(m[0])) continue;
    addFeat('https://www.lg.com' + m[0]);
  }

  // 2. /features/desktop/ directory (any locale)
  for (const m of html.matchAll(/https:\/\/www\.lg\.com\/content\/dam\/channel\/wcms\/[^"'\s?\\]+\/features\/desktop\/[^"'\s?\\]+\.jpg/gi)) {
    if (/thumbnail/i.test(m[0])) continue;
    addFeat(m[0].split('?')[0]);
  }
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/features\/desktop\/[^"'\s?\\]+\.jpg`, 'gi'))) {
    if (/thumbnail/i.test(m[0])) continue;
    addFeat('https://www.lg.com' + m[0].split('?')[0]);
  }

  // 3. Single-letter desktop suffix: -d.jpg / -D.jpg / _d.jpg / _D.jpg inside /features/
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/features\/[^"'\s?\\]+[-_][dD]\.(jpg|png)`, 'gi'))) {
    if (/thumbnail|-icon|[-_][mM]\.|mobilezoom/i.test(m[0])) continue;
    addFeat('https://www.lg.com' + m[0].split('?')[0]);
  }

  // 4. HA prefix style: D\d\d_...-D.jpg or M\d\d_... (dryer, washer)
  //    e.g. D01_Dryer-NA-Vivace-...-Intro-D.jpg  ← keep (Desktop)
  //         M01_Dryer-NA-Vivace-...-Intro-M.jpg  ← skip (Mobile)
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/features\/D\d+_[^"'\s?\\]+-D\d*\.jpg`, 'gi'))) {
    if (/thumbnail|-icon/i.test(m[0])) continue;
    addFeat('https://www.lg.com' + m[0].split('?')[0]);
  }

  // 5. -desktop-vari-NN.jpg (fridge new-style)
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/features\/[^"'\s?\\]+-desktop-vari-\d+\.jpg`, 'gi'))) {
    if (/thumbnail|-icon|-mobile/i.test(m[0])) continue;
    addFeat('https://www.lg.com' + m[0].split('?')[0]);
  }

  // 6. XBoom/GRAB: -desktop-NN- in filename inside /features/
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/features\/[^"'\s?\\]*-desktop-\d+[^"'\s?\\]*\.jpg`, 'gi'))) {
    if (/thumbnail|-icon|-mobile/i.test(m[0])) continue;
    addFeat('https://www.lg.com' + m[0].split('?')[0]);
  }

  // 7. /feature/desktop/ path (GRAB variant — note: singular "feature")
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/feature\/desktop\/[^"'\s?\\]+\.jpg`, 'gi'))) {
    if (/thumbnail|-icon/i.test(m[0])) continue;
    addFeat('https://www.lg.com' + m[0].split('?')[0]);
  }

  // 7b. DE/EU locale: {locale}/{model_id}/feature/{name}-d.jpg (desktop) or no suffix (standalone)
  //     e.g. /content/dam/channel/wcms/de/gbg5160cev/feature/...-feature-01-intro-d.jpg
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/feature\/[^"'\s?\\]+-d\.(jpg|png)`, 'gi'))) {
    if (/thumbnail|-icon|-mobile/i.test(m[0])) continue;
    addFeat('https://www.lg.com' + m[0].split('?')[0]);
  }
  // DE standalone feature images (no -d/-m/-t suffix, e.g. feature-09-door-cooling.jpg)
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/feature\/[^"'\s?\\]+\.(?:jpg|png)`, 'gi'))) {
    if (FEAT_SKIP.test(m[0])) continue;
    if (/[-_][mMtT]\d*\.(?:jpg|png)$/i.test(m[0])) continue; // skip mobile/tablet (incl. -m123.jpg)
    addFeat('https://www.lg.com' + m[0].split('?')[0]);
  }

  // 8. _D.jpg suffix outside /features/ dir (some HA products)
  for (const m of html.matchAll(new RegExp(LC + String.raw`images\/[^"'\s?\\]+[-_][Dd]\.(?:jpg|png)`, 'gi'))) {
    if (/thumbnail|-icon|[-_][Mm]\.|[-_][Mm]_/i.test(m[0])) continue;
    addFeat('https://www.lg.com' + m[0].split('?')[0]);
  }

  // 9. Flat: -feature-NN-...-d.jpg or -d_v.jpg (any locale, any case)
  for (const m of html.matchAll(new RegExp(LC + String.raw`images\/[^"'\s?\\]+-(?:feature-)?\d+[^"'\s?\\]*[-_][dD](?:_[vV])?\.jpg`, 'gi'))) {
    if (/thumbnail|-icon|[-_][mM]\.|-mobile|[-_][mM]_[vV]/i.test(m[0])) continue;
    addFeat('https://www.lg.com' + m[0].split('?')[0]);
  }

  // 10. Catch-all: any image in /features/ folder not yet captured
  //   Handles products where feature images have no -D/-d suffix (e.g. 03_Easy-to-Control_Dust_Bin.jpg)
  //   FEAT_SKIP and seen-set dedup prevent mobile/duplicate entries
  for (const m of html.matchAll(new RegExp(LC + String.raw`[^"'\s?\\]+\/features\/[^"'\s?\\]+\.(?:jpg|png)`, 'gi'))) {
    if (/thumbnail|-icon|mobilezoom/i.test(m[0])) continue;
    addFeat('https://www.lg.com' + m[0].split('?')[0]);
  }

  // Sort by sequence number in filename (e.g. -01-, -02-, D01_, D02_)
  raw.sort((a, b) => {
    const na = parseInt((a.match(/(?:^|\/)[DdMm]?(\d{2})[-_]/) || a.match(/-(\d{2})-/) || [, '99'])[1]);
    const nb = parseInt((b.match(/(?:^|\/)[DdMm]?(\d{2})[-_]/) || b.match(/-(\d{2})-/) || [, '99'])[1]);
    return na - nb;
  });

  return raw.slice(0, 20).map(path => {
    const type = featType(path);
    const relPath = path.replace('https://www.lg.com', '');
    const idx  = html.indexOf(relPath);
    const snip = idx >= 0 ? html.slice(idx, idx + 5000) : '';

    let title = '', desc = '';
    if (snip) {
      const tm = snip.match(/cmp-title__text[^>]*>([\s\S]*?)<\/h[23456]>/i);
      if (tm) title = tm[1].replace(/<[^>]+>/g, '').trim();
      const bm = snip.match(/c-text-contents__bodycopy[\s\S]{0,600}?<p>([\s\S]*?)<\/p>/i);
      if (bm) desc = bm[1].replace(/<[^>]+>/g, '').trim();
    }
    const fn = path.split('/').pop().replace(/^[DdMm]\d+_/, '').replace(/[-_][dDmM](_\d+)?\.(?:jpg|png)$/i, '');
    if (!title && type === 'feature') {
      title = fn.replace(/^[^-]+-\d+-\d*-?/, '').replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()).trim();
    }
    if (!desc && title) desc = title;

    return { a: title || fn, p: path, t: title.substring(0, 100), d: desc.substring(0, 300), w: 1600, h: 900, type };
  });
}

// ─── Specs ────────────────────────────────────────────────────────
function extractSpecs(html) {
  const sp = {};
  // Primary: c-compare-selling__spec-name / spec-desc pairs
  for (const m of html.matchAll(/c-compare-selling__spec-name[^>]*><p>([\s\S]*?)<\/p>[\s\S]*?c-compare-selling__spec-desc[^>]*><p>([\s\S]*?)<\/p>/g)) {
    const k = m[1].replace(/<[^>]+>/g, '').trim().replace(/[\s\t]+/g, '_');
    const v = m[2].replace(/<[^>]+>/g, '').trim();
    if (k && v && k.length < 80 && !sp[k]) sp[k] = v;
  }
  // Fallback: spec table rows
  if (!Object.keys(sp).length) {
    for (const m of html.matchAll(/<tr[\s\S]{0,500}?<th[^>]*>([\s\S]*?)<\/th>[\s\S]{0,500}?<td[^>]*>([\s\S]*?)<\/td>/g)) {
      const k = m[1].replace(/<[^>]+>/g, '').trim().replace(/\s+/g, '_');
      const v = m[2].replace(/<[^>]+>/g, '').trim();
      if (k && v && k.length < 80 && v.length < 300 && !sp[k]) sp[k] = v;
    }
  }
  return sp;
}

// ─── Main crawl endpoint ──────────────────────────────────────────
app.post('/api/crawl-product', async (req, res) => {
  const { url } = req.body;
  if (!url || !url.includes('lg.com')) {
    return res.status(400).json({ error: 'LG.com URL이 필요합니다.' });
  }

  try {
    console.log(`[crawl] ${url}`);

    const resp = await axios.get(url, {
      timeout: 35000,
      headers: {
        'User-Agent': UA,
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      }
    });
    const html = resp.data;

    // Product ID
    const urlParts = new URL(url).pathname.split('/').filter(Boolean);
    const id = urlParts[urlParts.length - 1].toUpperCase();

    // Metadata
    let nm = id, pr = '', op = '';
    for (const m of html.matchAll(/<script[^>]+type="application\/ld\+json"[^>]*>([\s\S]+?)<\/script>/gi)) {
      try {
        const jld = JSON.parse(m[1]);
        const nodes = jld['@graph'] ? jld['@graph'] : [jld];
        const product = nodes.find(n => n['@type'] === 'Product' || n['@type'] === 'product');
        if (product) {
          nm = product.name || nm;
          const offer = Array.isArray(product.offers) ? product.offers[0] : product.offers;
          if (offer) {
            const cur = offer.priceCurrency || 'SAR';
            const curSym = cur === 'USD' ? '$' : cur === 'EUR' ? '€' : cur === 'GBP' ? '£' : cur === 'SAR' ? 'SAR ' : (cur + ' ');
            if (offer.price) pr = `${curSym}${offer.price}`;
            if (offer.priceSpecification?.price) op = `${curSym}${offer.priceSpecification.price}`;
          }
          break;
        }
      } catch (_) {}
    }
    if (nm === id) {
      const ogM = html.match(/<meta[^>]+property="og:title"[^>]+content="([^"]+)"/i)
               || html.match(/<meta[^>]+content="([^"]+)"[^>]+property="og:title"/i);
      if (ogM) nm = ogM[1].replace(/\s*\|\s*.+$/, '').replace(/\s*-\s*[A-Z0-9][A-Z0-9\-]{4,}$/, '').trim();
    }
    if (nm === id) {
      const tm = html.match(/<title>([^<]+)<\/title>/i);
      if (tm) nm = tm[1].replace(/\s*[-|].*$/, '').trim();
    }

    // Non-English locale: fetch English name from SA EN
    const localeM = url.match(/lg\.com\/([a-z]{2,5}(?:_[a-z]{2})?)\//i);
    const locale  = localeM ? localeM[1].toLowerCase() : '';
    const isEn    = /^(sa_en|us|gb_en|ca_en|au|global_en|uk)/.test(locale);
    if (!isEn && locale) {
      try {
        const catMap = {
          monitore: 'monitors', fernseher: 'tvs', televisori: 'tvs', televisores: 'tvs',
          kuehlschraenke: 'refrigerators', refrigerateurs: 'refrigerators',
          waschmaschinen: 'washing-machines', lavadoras: 'washing-machines',
          soundbars: 'soundbars', lautsprecher: 'speakers', altavoces: 'speakers',
          klimaanlagen: 'air-conditioners', moniteurs: 'monitors', monitores: 'monitors',
        };
        let enPath = urlParts.slice(1).join('/').toLowerCase();
        for (const [local, en] of Object.entries(catMap)) enPath = enPath.replace(local, en);
        const enUrl  = `https://www.lg.com/sa_en/${enPath}`;
        const enResp = await axios.get(enUrl, { timeout: 12000, headers: { 'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9' } });
        const enHtml = enResp.data;
        let enNm = '';
        for (const m of enHtml.matchAll(/<script[^>]+type="application\/ld\+json"[^>]*>([\s\S]+?)<\/script>/gi)) {
          try {
            const jld  = JSON.parse(m[1]);
            const nodes = jld['@graph'] ? jld['@graph'] : [jld];
            const prod = nodes.find(n => n['@type'] === 'Product' || n['@type'] === 'product');
            if (prod && prod.name) { enNm = prod.name; break; }
          } catch (_) {}
        }
        if (!enNm) {
          const ogM = enHtml.match(/<meta[^>]+property="og:title"[^>]+content="([^"]+)"/i)
                   || enHtml.match(/<meta[^>]+content="([^"]+)"[^>]+property="og:title"/i);
          if (ogM) enNm = ogM[1].replace(/\s*\|\s*.+$/, '').replace(/\s*-\s*[A-Z0-9][A-Z0-9\-]{4,}$/, '').trim();
        }
        if (enNm && enNm !== id) { nm = enNm; console.log(`[crawl] EN name from sa_en: ${enNm}`); }
      } catch (_) { /* silent — keep original name */ }
    }

    // Price fallback for US site (no JSON-LD offers — price in HTML)
    if (!pr && locale === 'us') {
      // Try: find the model ID in inline JSON, then grab its price
      const idUpper = id.toUpperCase();
      const idRegion = (() => {
        const idx = html.indexOf(idUpper);
        return idx >= 0 ? html.slice(Math.max(0, idx - 200), idx + 500) : '';
      })();
      if (idRegion) {
        const nearPr = idRegion.match(/"(?:price|regularPrice|salePrice)"\s*:\s*"?([\d]+(?:\.\d{1,2})?)"?/);
        if (nearPr) pr = `$${parseFloat(nearPr[1]).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      }
      // Broader fallback: first price in JSON-like context
      if (!pr) {
        const anyPr = html.match(/"(?:regularPrice|listPrice)"\s*:\s*"?([\d]+(?:\.\d{1,2})?)"?/);
        if (anyPr) pr = `$${parseFloat(anyPr[1]).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      }
    }

    const cat  = catFromUrl(url);
    const gal  = extractGallery(html, nm, id);
    const feat = extractFeatures(html, id, locale);
    const sp   = extractSpecs(html);

    const bul = feat.slice(0, 5).map(f => {
      const t = (f.t || '').toUpperCase().substring(0, 50);
      return `${t} — ${(f.d || '').substring(0, 200)}`.trim();
    }).filter(b => b.length > 5);

    const product = {
      id, nm, cat, sub: cat,
      dv: ['TV', 'Audio'].includes(cat) ? 'MS' : 'HA',
      pr, op, url, crawled: true,
      gal, feat, sp, bul,
      tags: [], faq: [], promo: [], disc: [],
      kw: [id, 'LG', cat, nm].join(' ').substring(0, 250),
      geo: locale === 'de' ? 'de' : locale === 'uk' ? 'uk' : locale === 'mx' ? 'mx' : locale === 'ae' ? 'ae' : locale.startsWith('sa') ? '' : ''
    };

    console.log(`[crawl] ✅ ${id} — gal:${gal.length} feat:${feat.length} sp:${Object.keys(sp).length}`);
    res.json({ product });

  } catch (err) {
    console.error('[crawl-product] Error:', err.message);
    if (err.code === 'ECONNABORTED' || err.code === 'ETIMEDOUT') {
      return res.status(504).json({ error: '크롤링 타임아웃 (35s). LG.com 응답 없음.' });
    }
    if (err.response?.status === 403 || err.response?.status === 429) {
      return res.status(502).json({ error: `LG.com 접근 차단 (HTTP ${err.response.status}). 잠시 후 재시도.` });
    }
    res.status(500).json({ error: err.message || '크롤링 실패' });
  }
});

// ─── Static files ─────────────────────────────────────────────────
app.get('/', (req, res) => res.sendFile(__dirname + '/LG_AI_Content_Hub_v6_23.html'));
app.use(express.static(__dirname));

// ─── Start ────────────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log('');
  console.log('  ╔══════════════════════════════════════╗');
  console.log('  ║    CLIA Crawl Server  v1.4  ✅       ║');
  console.log(`  ║    http://localhost:${PORT}           ║`);
  console.log('  ╚══════════════════════════════════════╝');
  console.log('');
  console.log('  사용법:');
  console.log('  1. 이 창을 열어두세요 (닫으면 서버 종료)');
  console.log('  2. LG_AI_Content_Hub_v6_23.html 브라우저에서 열기');
  console.log('  3. Crawling 버튼 → Make 탭 → eBay 크롤 → URL 입력 → Crawl');
  console.log('');
});
