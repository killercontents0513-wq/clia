'use strict';
const fs = require('fs');
const html = fs.readFileSync('bulk_html/RNC7.html', 'utf-8');

// Gallery DZ pattern
const galSeen = new Set();
const galImgs = [];
// Match with relative /images/ prefix
for (const m of html.matchAll(/\/images\/[^"'\s?\\]+\/gallery\/DZ-(\d+)\.jpg/g)) {
  const key = '/content/dam/channel/wcms/sa_en' + m[0].split('?')[0];
  if (!galSeen.has(key)) { galSeen.add(key); galImgs.push({p:key, num:parseInt(m[1])}); }
}
// Match with full /content/dam/ prefix
for (const m of html.matchAll(/\/content\/dam\/channel\/wcms\/sa_en\/images\/[^"'\s?\\]+\/gallery\/DZ-(\d+)\.jpg/g)) {
  const key = m[0].split('?')[0];
  if (!galSeen.has(key)) { galSeen.add(key); galImgs.push({p:key, num:parseInt(m[1])}); }
}
galImgs.sort((a,b)=>a.num-b.num);
console.log('Gallery DZ:', galImgs.length, 'unique');
galImgs.slice(0,5).forEach(x=>console.log(' ', x.num, x.p.slice(-50)));

// Feature Desktop
const featSeen = new Set();
const featArr = [];
for (const m of html.matchAll(/\/images\/[^"'\s?\\]+\/features\/[^"'\s?\\]+-Desktop\.jpg/g)) {
  const key = '/content/dam/channel/wcms/sa_en' + m[0];
  if (!featSeen.has(key)) { featSeen.add(key); featArr.push(key); }
}
for (const m of html.matchAll(/\/content\/dam\/channel\/wcms\/sa_en\/images\/[^"'\s?\\]+\/features\/[^"'\s?\\]+-Desktop\.jpg/g)) {
  if (!featSeen.has(m[0])) { featSeen.add(m[0]); featArr.push(m[0]); }
}
console.log('Features Desktop:', featArr.length);
featArr.slice(0,5).forEach(p=>console.log(' ', p.slice(-60)));

// Feature title extraction for first feature
if (featArr.length > 0) {
  const path = featArr[0];
  const idx = html.indexOf(path.replace('/content/dam/channel/wcms/sa_en',''));
  const snip = idx >= 0 ? html.slice(idx, idx+5000) : '';
  const tm = snip.match(/cmp-title__text[^>]*>([\s\S]*?)<\/h[23456]>/i);
  const title = tm ? tm[1].replace(/<[^>]+>/g,'').trim() : '';
  const bm = snip.match(/c-text-contents__bodycopy[\s\S]{0,500}?<p>([\s\S]*?)<\/p>/i);
  const body = bm ? bm[1].replace(/<[^>]+>/g,'').trim() : '';
  console.log('feat[0] title:', title.substring(0,60));
  console.log('feat[0] body:', body.substring(0,80));
}

// Specs
const sp = {};
for (const m of html.matchAll(/c-compare-selling__spec-name[^>]*><p>([\s\S]*?)<\/p>[\s\S]*?c-compare-selling__spec-desc[^>]*><p>([\s\S]*?)<\/p>/g)) {
  const k = m[1].replace(/<[^>]+>/g,'').trim().replace(/\s+/g,'_');
  const v = m[2].replace(/<[^>]+>/g,'').trim();
  if (k && v) sp[k] = v;
}
console.log('Specs:', Object.keys(sp).length);
Object.entries(sp).slice(0,3).forEach(([k,v])=>console.log(' ', k.substring(0,30),'->', v.substring(0,40)));
