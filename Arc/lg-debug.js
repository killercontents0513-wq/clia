const puppeteer = require('puppeteer');

async function debug(url) {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
  await page.setViewport({ width: 1440, height: 900 });

  try { await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 }); }
  catch(e) {}
  await new Promise(r => setTimeout(r, 5000));

  const info = await page.evaluate(() => {
    // AEM 컴포넌트 구조 분석
    const aemSels = [
      '.c-hero-banner', '[class*="c-hero-banner"]',
      '[class*="c-floating"]', '[class*="c-text-contents"]',
      '[class*="cmp-teaser"]', '.cmp-teaser',
      '[class*="exp-"]', '[class*="pdp"]',
    ];
    const aemCounts = {};
    aemSels.forEach(s => { try { const n = document.querySelectorAll(s).length; if (n) aemCounts[s] = n; } catch(_) {} });

    // c-text-contents 구조에서 텍스트 추출
    const textBlocks = Array.from(document.querySelectorAll('[class*="c-text-contents"]'))
      .filter(el => el.offsetHeight > 30)
      .map(el => {
        const eyebrow = el.querySelector('[class*="eyebrow"]')?.innerText?.trim();
        const headline = el.querySelector('[class*="headline"] [class*="cmp-title"], [class*="headline"] h2, [class*="headline"] h3')?.innerText?.trim();
        const bodycopy = el.querySelector('[class*="bodycopy"] .cmp-text, [class*="bodycopy"] p')?.innerText?.trim();
        const allPs = Array.from(el.querySelectorAll('p')).map(p => p.innerText?.trim()).filter(t => t.length > 5);
        return { cls: el.className.substring(0, 60), eyebrow, headline, bodycopy: bodycopy?.substring(0, 150), allPs: allPs.slice(0, 5) };
      });

    // 이미지별 가장 가까운 cmp-text content 찾기  
    const imgWithCopy = Array.from(document.querySelectorAll('img'))
      .filter(img => img.offsetWidth > 200)
      .slice(0, 15)
      .map(img => {
        // 이미지의 조상 중 c-text-contents 찾기
        let cur = img.parentElement, found = null;
        while (cur && !found) {
          if ((cur.className || '').includes('c-text-contents') || 
              (cur.className || '').includes('c-hero-banner') ||
              (cur.className || '').includes('c-floating')) found = cur;
          cur = cur.parentElement;
        }
        if (!found) return null;
        const eyebrow = found.querySelector('[class*="eyebrow"]')?.innerText?.trim()?.substring(0, 80);
        const hl = found.querySelector('h2,h3,[class*="headline"]')?.innerText?.trim()?.substring(0, 80);
        const body = Array.from(found.querySelectorAll('p')).map(p => p.innerText?.trim()).filter(t => t.length > 10).join('\n').substring(0, 200);
        return { imgAlt: img.alt?.substring(0, 50), eyebrow, hl, body };
      }).filter(Boolean);

    // 모든 p 요소 (footnote 포함)
    const footnotePara = Array.from(document.querySelectorAll('p'))
      .filter(p => p.offsetHeight > 0 && p.innerText?.trim().startsWith('*'))
      .map(p => ({ cls: p.className, text: p.innerText.trim().substring(0, 150) }));

    return { aemCounts, textBlocks: textBlocks.slice(0, 8), imgWithCopy: imgWithCopy.slice(0, 6), footnotePara };
  });

  console.log('\n=== AEM 셀렉터 매칭 ===');
  Object.entries(info.aemCounts).forEach(([s,n]) => console.log(`  ${n}x ${s}`));

  console.log('\n=== c-text-contents 블록 ===');
  info.textBlocks.forEach((b, i) => {
    console.log(`\n[${i+1}] .${b.cls}`);
    if (b.eyebrow) console.log(`  eyebrow: "${b.eyebrow}"`);
    if (b.headline) console.log(`  headline: "${b.headline}"`);
    if (b.bodycopy) console.log(`  bodycopy: "${b.bodycopy}"`);
    if (b.allPs?.length) console.log(`  all p[${b.allPs.length}]: ${b.allPs.map(p => `"${p.substring(0,60)}"`).join(', ')}`);
  });

  console.log('\n=== 이미지 + 카피 매칭 ===');
  info.imgWithCopy.forEach((item, i) => {
    console.log(`\n[${i+1}] img: "${item.imgAlt}"`);
    if (item.eyebrow) console.log(`  eyebrow: "${item.eyebrow}"`);
    if (item.hl) console.log(`  headline: "${item.hl}"`);
    if (item.body) console.log(`  body: "${item.body}"`);
  });

  console.log('\n=== Footnote (*) ===');
  info.footnotePara.forEach(f => console.log(`  .${f.cls}: "${f.text}"`));

  await browser.close();
}

debug(process.argv[2] || 'https://www.lg.com/uk/laundry/washer-dryers/fwy706gbtn1/').catch(console.error);
