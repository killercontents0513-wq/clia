'use strict';
const axios = require('axios');

(async () => {
  const r = await axios.get('https://www.lg.com/sa_en/speakers/party-speakers/rnc7/', {
    timeout: 30000,
    headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' }
  });
  const html = r.data;
  const CDN = 'https://www.lg.com/content/dam/channel/wcms/sa_en';

  // Gallery
  const seen = new Set(), imgs = [];
  for (const m of html.matchAll(/\/images\/[^"'\s?\\]+\/gallery\/DZ-(\d+)\.jpg/g)) {
    const key = CDN + m[0].split('?')[0];
    if (!seen.has(key)) { seen.add(key); imgs.push({ p: key, num: parseInt(m[1]) }); }
  }
  for (const m of html.matchAll(/\/content\/dam\/channel\/wcms\/sa_en\/images\/[^"'\s?\\]+\/gallery\/DZ-(\d+)\.jpg/g)) {
    const key = m[0].split('?')[0];
    if (!seen.has(key)) { seen.add(key); imgs.push({ p: key, num: parseInt(m[1]) }); }
  }
  console.log('Gallery unique DZ:', imgs.length);

  // Features
  const featSeen = new Set(), featRaw = [];
  for (const m of html.matchAll(/\/images\/[^"'\s?\\]+\/features\/[^"'\s?\\]+-Desktop\.jpg/g)) {
    if (/thumbnail/i.test(m[0])) continue;
    const key = CDN + m[0];
    if (!featSeen.has(key)) { featSeen.add(key); featRaw.push(key); }
  }
  for (const m of html.matchAll(/\/content\/dam\/channel\/wcms\/sa_en\/images\/[^"'\s?\\]+\/features\/[^"'\s?\\]+-Desktop\.jpg/g)) {
    if (/thumbnail/i.test(m[0])) continue;
    if (!featSeen.has(m[0])) { featSeen.add(m[0]); featRaw.push(m[0]); }
  }
  console.log('Features Desktop:', featRaw.length);
  featRaw.slice(0, 3).forEach(p => console.log(' ', p.slice(-60)));

  // Test title extraction for first feature
  if (featRaw.length > 0) {
    const path = featRaw[0];
    const relPath = path.replace(CDN, '');
    const idx = html.indexOf(relPath);
    const snip = idx >= 0 ? html.slice(idx, idx + 5000) : '';
    const tm = snip.match(/cmp-title__text[^>]*>([\s\S]*?)<\/h[23456]>/i);
    const title = tm ? tm[1].replace(/<[^>]+>/g, '').trim() : '';
    console.log('feat[0] title:', title.substring(0, 60));
  }

  // Specs
  const sp = {};
  for (const m of html.matchAll(/c-compare-selling__spec-name[^>]*><p>([\s\S]*?)<\/p>[\s\S]*?c-compare-selling__spec-desc[^>]*><p>([\s\S]*?)<\/p>/g)) {
    const k = m[1].replace(/<[^>]+>/g, '').trim().replace(/[\s\t]+/g, '_');
    const v = m[2].replace(/<[^>]+>/g, '').trim();
    if (k && v && k.length < 80) sp[k] = v;
  }
  console.log('Specs:', Object.keys(sp).length);
  Object.entries(sp).slice(0, 3).forEach(([k, v]) => console.log(' ', k.substring(0,20), '->', v.substring(0,40)));
})().catch(e => console.error(e.message));
