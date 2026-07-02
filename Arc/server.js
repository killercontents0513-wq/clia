require('dotenv').config({ override: true });
const express = require('express');
const cors = require('cors');
const puppeteer = require('puppeteer');
const Anthropic = require('@anthropic-ai/sdk');

const app = express();
// file:// 포함 모든 origin 허용 (CORS)
app.use(cors({ origin: (origin, cb) => cb(null, true), credentials: false }));
app.use(express.json());
app.use(express.static('.'));

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

/* ──────────────────────────────────────────
   1. PDP 크롤러
────────────────────────────────────────── */
async function crawlLGPDP(url) {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--disable-web-security',
    ]
  });
  try {
    const page = await browser.newPage();
    await page.setUserAgent(
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    );
    await page.setViewport({ width: 1440, height: 900 });

    // 1단계: domcontentloaded로 빠르게 로딩 (networkidle2 대신)
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
    } catch (e) {
      console.warn('Initial load warning (continuing):', e.message);
    }

    // 2단계: 쿠키 배너 닫기
    try {
      await page.waitForSelector(
        'button[id*="accept"], button[class*="accept"], #onetrust-accept-btn-handler, .cookie-accept',
        { timeout: 3000 }
      );
      await page.click('button[id*="accept"], button[class*="accept"], #onetrust-accept-btn-handler, .cookie-accept');
      await new Promise(r => setTimeout(r, 1000));
    } catch (_) { /* 쿠키 배너 없으면 무시 */ }

    // 3단계: 주요 콘텐츠 로딩 대기 (최대 15초)
    try {
      await page.waitForSelector(
        '[class*="feature"], [class*="benefit"], [class*="highlight"], .section-inner, main img',
        { timeout: 15000 }
      );
    } catch (_) { /* 없으면 무시 */ }

    // 4단계: 스크롤하여 lazy-load 이미지 트리거
    await page.evaluate(async () => {
      await new Promise(resolve => {
        let scrolled = 0;
        const step = 600;
        const timer = setInterval(() => {
          window.scrollBy(0, step);
          scrolled += step;
          if (scrolled >= document.body.scrollHeight) {
            clearInterval(timer);
            window.scrollTo(0, 0);
            resolve();
          }
        }, 150);
        // 최대 8초 후 강제 종료
        setTimeout(() => { clearInterval(timer); resolve(); }, 8000);
      });
    });

    // 5단계: 이미지 로딩 안정화 대기
    await new Promise(r => setTimeout(r, 2000));

    // Feature 섹션 + 전체 콘텐츠 구조 추출
    const data = await page.evaluate(() => {
      const result = {
        title: '',
        subtitle: '',
        modelName: '',
        features: [],
        specs: [],
        heroImages: []
      };

      // 제품명
      result.title =
        document.querySelector('h1.prod-title, h1.tit, .visual-area h1, h1')?.innerText?.trim() || '';
      result.subtitle =
        document.querySelector('.sub-tit, .visual-area .sub-title, h2')?.innerText?.trim() || '';
      result.modelName =
        document.querySelector('.model-name, .sku, [class*="model"]')?.innerText?.trim() || '';

      // Hero 이미지
      const heroImgs = document.querySelectorAll(
        '.visual-area img, .hero-area img, .kv-area img, [class*="hero"] img, [class*="visual"] img'
      );
      heroImgs.forEach(img => {
        if (img.src && !img.src.includes('icon') && !img.src.includes('logo')) {
          result.heroImages.push({ src: img.src, alt: img.alt || '', width: img.naturalWidth, height: img.naturalHeight });
        }
      });

      // Feature 섹션 추출
      // LG.com feature 섹션은 보통 .feature-group, .product-feature, [class*="feature"] 등
      const featureSections = document.querySelectorAll(
        '[class*="feature"], [class*="benefit"], [class*="reason"], [class*="highlight"], .section-inner, .cont-inner'
      );

      featureSections.forEach(section => {
        // 섹션 내 이미지
        const imgs = section.querySelectorAll('img');
        const sectionImages = [];
        imgs.forEach(img => {
          if (img.src && img.naturalWidth > 100 &&
            !img.src.includes('icon') && !img.src.includes('logo') &&
            !img.src.includes('svg')) {
            sectionImages.push({
              src: img.src,
              alt: img.alt || '',
              width: img.naturalWidth,
              height: img.naturalHeight,
              ratio: img.naturalWidth > 0 ? img.naturalWidth / img.naturalHeight : 1
            });
          }
        });

        // 섹션 내 텍스트
        const headings = Array.from(section.querySelectorAll('h2, h3, h4, strong, .tit, .title, [class*="title"], [class*="tit"]'))
          .map(el => el.innerText?.trim()).filter(t => t && t.length > 2 && t.length < 200);

        const bodies = Array.from(section.querySelectorAll('p, .desc, .txt, [class*="desc"], [class*="body"]'))
          .map(el => el.innerText?.trim()).filter(t => t && t.length > 5 && t.length < 1000);

        const bullets = Array.from(section.querySelectorAll('li'))
          .map(el => el.innerText?.trim()).filter(t => t && t.length > 2 && t.length < 300);

        if (sectionImages.length > 0 || headings.length > 0) {
          result.features.push({
            images: sectionImages,
            headings: [...new Set(headings)].slice(0, 3),
            bodies: [...new Set(bodies)].slice(0, 3),
            bullets: [...new Set(bullets)].slice(0, 6)
          });
        }
      });

      // 중복 제거 및 의미있는 섹션만
      const seen = new Set();
      result.features = result.features.filter(f => {
        const key = (f.headings[0] || '') + (f.images[0]?.src || '');
        if (seen.has(key) || key === '') return false;
        seen.add(key);
        return true;
      }).slice(0, 12);

      // Spec 테이블
      document.querySelectorAll('.spec-list li, .spec-table tr, [class*="spec"] li').forEach(row => {
        const label = row.querySelector('.tit, th, dt, [class*="label"]')?.innerText?.trim();
        const value = row.querySelector('.txt, td, dd, [class*="value"]')?.innerText?.trim();
        if (label && value) result.specs.push({ label, value });
      });

      return result;
    });

    return data;
  } finally {
    await browser.close();
  }
}

/* ──────────────────────────────────────────
   2. Claude API — 모듈 매핑
────────────────────────────────────────── */
async function generateModules(crawledData) {
  // Amazon A+ 모듈 정의 & 글자 수 제한
  const moduleGuide = `
Available Amazon A+ Content Modules and their text limits:

STANDARD MODULES:
- "standard-image-header": Full-width banner image (970×300). headline: 150 chars, body: 6000 chars
- "highlights": Left 300×300 image + center text (headline: 150, subhead×3: 80 each, body×3: 500 each) + right bullet list (header: 80, bullets: 200 each, max 8)
- "standard-four-image-text": 4 images (180×180 each). module_headline: 150, per image: title 80, body 300
- "standard-three-image-text": 3 images (310×300 each). module_headline: 150, per image: title 80, body 150
- "standard-single-left-image": Large image left (300×400), text right. headline: 160, body: 6000
- "standard-single-right-image": Large image right (300×400), text left. headline: 160, body: 6000
- "standard-text": Text only. headline: 150 (optional), body: 6000
- "standard-tech-specs": Spec table, 4-16 rows. column headers + spec rows (label+value pairs)
- "standard-comparison-table": 3-product comparison. headline: 80, features: max 5

Use these to map LG PDP content into an ordered list of A+ modules.

Rules:
- Landscape image (ratio > 1.2): use standard-image-header, highlights, standard-four-image-text, standard-three-image-text
- Portrait image (ratio < 0.85): use standard-single-left-image or standard-single-right-image
- Square image (ratio 0.85~1.2): use highlights, standard-four-image-text
- Text with bullet list: use highlights
- Multiple feature images (3-4): use standard-three-image-text or standard-four-image-text
- If specs available: add standard-tech-specs at end
- Alternate left/right image placement for visual rhythm
- Keep original text as close as possible; only trim if over character limit
`;

  const prompt = `You are an Amazon A+ Content specialist for LG Electronics.

Based on the crawled LG.com PDP data below, generate an ordered list of Amazon A+ content modules.

${moduleGuide}

CRAWLED PDP DATA:
${JSON.stringify(crawledData, null, 2)}

Return a JSON array of modules in this exact format:
[
  {
    "moduleId": "highlights",
    "headline": "...",
    "subheads": ["...", "...", "..."],
    "bodies": ["...", "...", "..."],
    "bulletTitle": "...",
    "bullets": ["...", "...", "..."],
    "imageUrl": "https://...",
    "imageAlt": "...",
    "imageRatio": "landscape|portrait|square"
  },
  {
    "moduleId": "standard-image-header",
    "headline": "...",
    "body": "...",
    "imageUrl": "https://...",
    "imageAlt": "..."
  },
  ...
]

Fields vary by moduleId:
- standard-image-header: moduleId, headline, body, imageUrl, imageAlt
- highlights: moduleId, headline, subheads[], bodies[], bulletTitle, bullets[], imageUrl, imageAlt
- standard-four-image-text: moduleId, headline, items[{imageUrl, imageAlt, title, body}]
- standard-three-image-text: moduleId, headline, items[{imageUrl, imageAlt, title, body}]
- standard-single-left-image: moduleId, headline, body, imageUrl, imageAlt
- standard-single-right-image: moduleId, headline, body, imageUrl, imageAlt
- standard-text: moduleId, headline, body
- standard-tech-specs: moduleId, specs[{label, value}]

IMPORTANT:
- Only return valid JSON array, no markdown, no explanation
- Use actual image URLs from the crawled data
- Keep text as close to original as possible
- Truncate only if exceeding character limits
- Generate 5-8 modules minimum`;

  const message = await client.messages.create({
    model: 'claude-haiku-4-5',
    max_tokens: 4096,
    messages: [{ role: 'user', content: prompt }]
  });

  const text = message.content[0].text.trim();
  // JSON만 추출
  const jsonMatch = text.match(/\[[\s\S]*\]/);
  if (!jsonMatch) throw new Error('Claude returned non-JSON response');
  return JSON.parse(jsonMatch[0]);
}

/* ──────────────────────────────────────────
   3. API 엔드포인트
────────────────────────────────────────── */
app.post('/api/generate', async (req, res) => {
  const { url } = req.body;
  if (!url) return res.status(400).json({ error: 'URL is required' });

  console.log(`\n[1/3] Crawling: ${url}`);
  try {
    const crawledData = await crawlLGPDP(url);
    console.log(`[2/3] Crawled ${crawledData.features.length} feature sections`);

    const modules = await generateModules(crawledData);
    console.log(`[3/3] Generated ${modules.length} A+ modules`);

    res.json({ success: true, modules, crawledData });
  } catch (err) {
    console.error('Error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// Health check
app.get('/api/health', (req, res) => res.json({ ok: true }));

/* ──────────────────────────────────────────
   /api/analyze  — LG.com PDP 섹션 추출
   Claude 없이 크롤링만 수행, 섹션 순서 보존
────────────────────────────────────────── */
app.post('/api/analyze', async (req, res) => {
  const { url } = req.body;
  if (!url) return res.status(400).json({ error: 'url required' });

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox',
           '--disable-blink-features=AutomationControlled', '--disable-web-security',
           '--lang=en-US,en']
  });
  try {
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    await page.setViewport({ width: 1440, height: 900 });
    await page.setExtraHTTPHeaders({ 'Accept-Language': 'en-US,en;q=0.9' });

    // ① 페이지 로드 (networkidle 실패 허용)
    try {
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
    } catch (e) {
      console.warn('goto networkidle2 warning, retrying domcontentloaded:', e.message);
      try { await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
      catch (e2) { console.warn('goto domcontentloaded warning (continuing):', e2.message); }
    }

    // ② JS 렌더링 대기 (SPA hydration)
    await new Promise(r => setTimeout(r, 4000));

    // ③ 404 / 에러 페이지 감지 (LG SPA는 URL 유지, DOM에 에러 표시)
    const finalUrl = page.url();
    const pageTitle = await page.title().catch(() => '');
    const titleLower = pageTitle.toLowerCase();

    // H1 텍스트 + LG 전용 에러 클래스 감지
    const pageCheck = await page.evaluate(() => {
      const h1 = document.querySelector('h1')?.innerText?.trim() || '';
      // LG 전용: error-common class
      const hasLGError = !!document.querySelector('.error-common, #lgContents.error-common, [class*="error-common"]');
      // 에러 페이지 키워드
      const body100 = document.body?.innerText?.substring(0, 200) || '';
      return { h1, hasLGError, body100 };
    }).catch(() => ({ h1: '', hasLGError: false, body100: '' }));

    const h1Lower = pageCheck.h1.toLowerCase();
    const bodyLower = pageCheck.body100.toLowerCase();

    const is404 =
      pageCheck.hasLGError ||
      titleLower.includes("404") ||
      titleLower.includes("not found") ||
      h1Lower.includes("we're sorry") ||
      h1Lower.includes("page you requested") ||
      h1Lower.includes("not available") ||
      h1Lower.includes("page not found") ||
      (bodyLower.includes("we're sorry") && bodyLower.includes("page"));

    if (is404) {
      return res.status(400).json({
        error: `페이지를 찾을 수 없습니다. URL을 확인해주세요.\n(URL: ${finalUrl})`
      });
    }
    console.log(`[analyze] 페이지 로드: ${finalUrl} | ${pageTitle} | H1: ${pageCheck.h1.substring(0, 60)}`);

    // ③-b lazy-load 이미지 강제 활성화 (IntersectionObserver 미작동 대비)
    try {
      await page.evaluate(() => {
        // LG AEM placeholder 패턴 감지 (transparent.png 등 비표준 포함)
        function isPlaceholderSrc(img) {
          const curSrc = img.getAttribute('src') || '';
          if (!curSrc || img.naturalWidth <= 1) return true;
          return /blank|placeholder|transparent|spacer|1x1|\/common\/|loading/i.test(curSrc)
              || curSrc.endsWith('.gif');
        }
        document.querySelectorAll('img').forEach(img => {
          ['data-src','data-lazy-src','data-original','data-lazy','data-srcset','data-lazy-srcset'].forEach(attr => {
            const val = img.getAttribute(attr);
            if (!val) return;
            if (attr.includes('srcset')) { if (!img.srcset) img.srcset = val; return; }
            if (isPlaceholderSrc(img)) img.src = val;
          });
        });
        document.querySelectorAll('source').forEach(src => {
          const lazy = src.getAttribute('data-srcset') || src.getAttribute('data-src') || '';
          if (lazy && !src.srcset) src.srcset = lazy;
        });
      });
    } catch (e) { console.warn('Force lazy-load warning:', e.message); }

    // ④ 쿠키/동의 배너 강제 제거
    try {
      await page.evaluate(() => {
        const COOKIE_SELS = [
          '#onetrust-consent-sdk', '#onetrust-banner-sdk', '#onetrust-pc-sdk',
          '[id*="onetrust"]', '[class*="onetrust"]',
          '[id*="cookie"]', '[class*="cookie-banner"]', '[class*="cookie-consent"]',
          '[id*="consent"]', '[class*="consent-"]',
          '[aria-label*="cookie" i]', '[aria-label*="consent" i]',
          '.ReactModal__Overlay', '.modal-overlay',
        ];
        COOKIE_SELS.forEach(sel => {
          try { document.querySelectorAll(sel).forEach(el => el.remove()); } catch (_) {}
        });
        // position:fixed 고zIndex 오버레이 제거
        document.querySelectorAll('*').forEach(el => {
          try {
            const s = window.getComputedStyle(el);
            if ((s.position === 'fixed' || s.position === 'sticky') &&
                +s.zIndex > 500 && el.offsetHeight > 80) el.remove();
          } catch (_) {}
        });
        document.body.style.overflow = 'auto';
      });
    } catch (e) { console.warn('Cookie removal warning:', e.message); }

    // ⑤ 스크롤 → lazy-load 이미지 활성화 (페이지 이탈 대비 try/catch)
    try {
      await page.evaluate(async () => {
        await new Promise(resolve => {
          let pos = 0;
          const step = 400;
          const t = setInterval(() => {
            window.scrollBy(0, step);
            pos += step;
            if (pos >= document.body.scrollHeight) {
              clearInterval(t);
              window.scrollTo(0, 0);
              resolve();
            }
          }, 100);
          setTimeout(() => { clearInterval(t); resolve(); }, 12000);
        });
      });
      // 스크롤 후 재차 lazy-load 강제 실행 (스크롤로 IntersectionObserver 트리거 후 data-src 잔여분 처리)
      await page.evaluate(() => {
        function isPlaceholderSrc(img) {
          const curSrc = img.getAttribute('src') || '';
          if (!curSrc || img.naturalWidth <= 1) return true;
          return /blank|placeholder|transparent|spacer|1x1|\/common\/|loading/i.test(curSrc)
              || curSrc.endsWith('.gif');
        }
        document.querySelectorAll('img').forEach(img => {
          ['data-src','data-lazy-src','data-original','data-lazy'].forEach(attr => {
            const val = img.getAttribute(attr);
            if (val && isPlaceholderSrc(img)) img.src = val;
          });
        });
        document.querySelectorAll('source').forEach(src => {
          const lazy = src.getAttribute('data-srcset') || src.getAttribute('data-src') || '';
          if (lazy && !src.srcset) src.srcset = lazy;
        });
      });
      await new Promise(r => setTimeout(r, 3000)); // 이미지 로딩 안정화 (2s → 3s)
    } catch (e) {
      console.warn('Scroll warning (continuing):', e.message);
      await new Promise(r => setTimeout(r, 1500));
    }

    // ⑤-b 캐러셀/슬라이더 숨겨진 슬라이드 이미지 수집
    // ⚠️ position/left/top/transform 변경 금지:
    //    변경 시 슬라이드가 수직으로 쌓여 컨테이너 height 폭발 → Strategy 1 필터 제거됨
    //    → 개별 슬라이드가 독립 섹션으로 추출, 그루핑(cardItems) 로직이 작동 안 됨
    try {
      await page.evaluate(() => {
        // display:none인 슬라이드만 block으로 전환 (position/transform은 절대 변경 안 함)
        [
          '[class*="swiper-slide"]', '[class*="slick-slide"]',
          '[class*="carousel-item"]', '[class*="owl-item"]',
          '[class*="-slide"]', '[role="tabpanel"]',
          '[aria-roledescription="slide"]',
          '[class*="tab-content"]', '[class*="tab-panel"]',
        ].forEach(sel => {
          document.querySelectorAll(sel).forEach(el => {
            const cs = window.getComputedStyle(el);
            // display:none만 block으로 전환 (그 외 상태는 건드리지 않음)
            if (cs.display === 'none') el.style.setProperty('display', 'block', 'important');
            // visibility/opacity만 조정 (이미지 로딩 트리거용)
            el.style.setProperty('visibility', 'visible', 'important');
            el.style.setProperty('opacity', '1', 'important');
            // ❌ position, left, top, transform → 변경 금지
          });
        });
        // ❌ 래퍼 overflow/transform 변경 금지 (height 왜곡 원인 제거)

        // 새롭게 활성화된 슬라이드의 lazy 이미지 src 직접 주입
        function isPlaceholderSrc(img) {
          const curSrc = img.getAttribute('src') || '';
          if (!curSrc || img.naturalWidth <= 1) return true;
          return /blank|placeholder|transparent|spacer|1x1|\/common\/|loading/i.test(curSrc)
              || curSrc.endsWith('.gif');
        }
        document.querySelectorAll('img').forEach(img => {
          ['data-src', 'data-lazy-src', 'data-original', 'data-lazy'].forEach(attr => {
            const val = img.getAttribute(attr);
            if (val && isPlaceholderSrc(img)) img.src = val;
          });
          const lazySrcset = img.getAttribute('data-srcset') || img.getAttribute('data-lazy-srcset') || '';
          if (lazySrcset && !img.srcset) img.srcset = lazySrcset;
        });
        document.querySelectorAll('source').forEach(src => {
          const lazy = src.getAttribute('data-srcset') || src.getAttribute('data-src') || '';
          if (lazy && !src.srcset) src.srcset = lazy;
        });
      });
      await new Promise(r => setTimeout(r, 2500)); // 슬라이드 이미지 로딩 대기
    } catch (e) {
      console.warn('Carousel force warning:', e.message);
    }

    // ⑥ DOM 분석
    const features = await page.evaluate(() => {

      // ── 헬퍼 함수 ──────────────────────────────────────
      const SKIP_KW = [
        // 쿠키/동의
        'cookie', 'consent', 'privacy policy', 'manage preference',
        'we use cookies', 'gdpr', 'terms of use',
        // 계정/인증
        'sign in', 'sign up', 'log in', 'create account', 'register',
        'newsletter', 'subscribe',
        // 네비게이션
        'navigation', 'skip to', 'go to homepage', "can't find",
        "page you requested", "page isn't available",
        'search', 'cart', 'checkout', 'wishlist',
        'breadcrumb', 'page not', "we're sorry",
        // 목록 UI
        'view all', 'see all', 'load more', 'show more',
        'sort by', 'filter', 'results',
        // 리뷰/서포트/연락처
        'write a review', 'customer review', 'questions?', 'let us help',
        'contact us', 'find locally', 'find nearby', 'store locator',
        'find a store', 'product support', 'manuals',
        // e-커머스 노이즈
        'limited quantity', 'almost sold out', 'add to cart',
        'summary-member', 'buy now', 'shop now',
        // 추천/관련상품
        'recommended product', 'related product', 'you may also',
        'customers also', 'people also',
        // 리뷰/폼
        'required field', 'ratings', 'write your review', 'overall rating',
        // 기타 노이즈
        'find locally', 'find nearby', 'geolocation',
        'get directions', 'directions to',
        'summary-member', 'limited quantity',
        'limited time', 'offer expires',
        'check your final price', 'final price',
        'what people are saying', 'customer rating',
        'be the first to review', 'first to review',
        'add to compare', 'remove compare',
        'to properly experience', 'use an alternate browser',
        'response to coronavirus', 'covid',
        'passwords must', 'characters left',
        'component-obs', 'iw_component', 'component-update',
        'learn more', // 단독으로 오는 경우
        // AR/360° 뷰어 UI 노이즈
        'experience this product around', 'ar experience',
        'view in your room', 'view in room', '360° view',
        // 소셜/공유 UI
        'share this page', 'share on', 'follow us',
        // 추천/프로모션/지원 노이즈
        'our picks for you', 'picks for you',
        'need more help', 'more help with your product',
        'discover our latest', 'latest promotions', 'latest offers',
        'see all promotions', 'view promotions',
      ];
      function isSkip(text) {
        // \xa0(non-breaking space), \t 등 공백 정규화
        const t = (text || '').replace(/[\xa0\t]+/g, ' ').toLowerCase().trim();
        return SKIP_KW.some(kw => t.includes(kw));
      }

      // CSS 클래스 이름처럼 보이는 텍스트 감지
      // e.g. "component-update-nickname-title", "component-OBScountrySelectDesc"
      function looksLikeClassName(text) {
        if (!text) return false;
        const t = text.trim();
        // 공백 없고 하이픈+영숫자 패턴 (kebab-case or camelCase+hyphen)
        if (/^[a-zA-Z][a-zA-Z0-9]*(-[a-zA-Z0-9]+){1,}$/.test(t)) return true;
        // 전체가 camelCase (소문자시작 + 대문자 섞임, 공백 없음)
        if (/^[a-z][a-z0-9]*[A-Z][a-zA-Z0-9]+$/.test(t)) return true;
        return false;
      }

      // 네비게이션 카테고리 목록처럼 보이는 불릿 감지
      function looksLikeNavBullet(text) {
        if (!text) return false;
        // \n\t\n 패턴 (메뉴 항목) 또는 너무 많은 줄바꿈
        if ((text.match(/\n/g) || []).length > 3) return true;
        // TV/AUDIO/VIDEO 같은 카테고리 패턴
        if (/^[A-Z\/&]+(\s[A-Z\/&]+)*$/.test(text.trim())) return true;
        return false;
      }

      // ── 상대 URL → 절대 URL 변환 (핵심 버그 수정) ──────────────
      function abs(u) {
        if (!u) return '';
        u = u.trim();
        if (u.startsWith('data:') || u.startsWith('blob:')) return u;
        if (u.startsWith('//')) return location.protocol + u;
        if (u.startsWith('/'))  return location.origin + u;
        if (!u.startsWith('http')) {
          try { return new URL(u, location.href).href; } catch (_) {}
        }
        return u;
      }

      // srcset 문자열에서 최고 해상도 URL 파싱 (w디스크립터·x디스크립터 모두 지원)
      function parseBestSrcset(ss) {
        if (!ss) return '';
        let bestScore = -1, bestUrl = '';
        ss.split(',').forEach(part => {
          const tokens = part.trim().split(/\s+/);
          const u = tokens[0];
          if (!u) return;
          const descriptor = tokens[1] || '';
          let score = 0;
          if (/^\d+w$/i.test(descriptor)) {
            score = parseInt(descriptor);            // 1440w → 1440
          } else if (/^[\d.]+x$/i.test(descriptor)) {
            score = parseFloat(descriptor) * 1000;  // 2x → 2000 (w보다 낮은 우선순위)
          } else {
            score = 500; // 디스크립터 없는 단독 URL → 중간 우선순위
          }
          if (score > bestScore) { bestScore = score; bestUrl = u; }
        });
        return abs(bestUrl);
      }

      // src가 placeholder(투명 1px 등)인지 판별
      function isSrcPlaceholder(img) {
        const src = img.getAttribute('src') || img.src || '';
        if (!src) return true;
        if (img.naturalWidth <= 1) return true; // 1×1 투명 png / 아직 미로드(0px)
        return /blank|placeholder|transparent|spacer|1x1|\/common\/|loading/i.test(src)
            || src.endsWith('.gif');
      }

      // srcset / picture에서 최고 해상도 URL 추출
      function bestSrc(img) {
        // 1) <picture> 안의 <source srcset>에서 최적 해상도 선택
        //    srcset(IDL) 또는 data-srcset 모두 탐색 (lazy-load 전/후 모두 대응)
        const picture = img.closest('picture');
        if (picture) {
          const sources = Array.from(picture.querySelectorAll('source'));
          // jpg/webp 우선순위: webp → 타입 없음 → 나머지
          for (const preferType of ['image/webp', '', null]) {
            for (const src of sources) {
              if (preferType !== null && src.getAttribute('type') !== preferType) continue;
              const ss = src.srcset || src.getAttribute('srcset') || src.getAttribute('data-srcset') || '';
              const u = parseBestSrcset(ss);
              if (u) return u;
            }
          }
        }

        // 2) img의 srcset / data-srcset
        const imgSrcset = img.srcset || img.getAttribute('srcset') || img.getAttribute('data-srcset') || '';
        const fromSrcset = parseBestSrcset(imgSrcset);
        if (fromSrcset) return fromSrcset;

        // 3) data-src 우선 (naturalWidth ≤ 1 = placeholder or not-loaded → data-src가 실제 URL)
        const lazySrc = img.getAttribute('data-src') || img.getAttribute('data-lazy-src') ||
                        img.getAttribute('data-original') || img.getAttribute('data-lazy') || '';
        if (lazySrc && isSrcPlaceholder(img)) return abs(lazySrc);

        // 4) currentSrc (브라우저가 선택한 실제 URL)
        if (img.currentSrc && !isSrcPlaceholder(img)) return abs(img.currentSrc);

        // 5) src — placeholder 패턴 제외
        const src = img.src || '';
        if (src && !isSrcPlaceholder(img)) return abs(src);

        // 6) data-src fallback (placeholder이더라도 data-src 있으면 사용)
        if (lazySrc) return abs(lazySrc);

        // 7) src 속성 최후 fallback
        return abs(img.getAttribute('src') || '');
      }

      // 이미지와 가장 인접한 텍스트(heading/caption/desc) 추출
      function findNearImageText(img, root) {
        // 0) AEM: c-hero-banner 구조 — 이미지와 텍스트가 형제 컨테이너에 분리
        //    img → .c-hero-banner__media → .c-hero-banner → .c-hero-banner__content → .c-text-contents
        let cur = img.parentElement;
        for (let i = 0; i < 6; i++) {
          if (!cur || cur === root) break;
          const cls = cur.className || '';
          // AEM banner / floating-contents 컨테이너 감지
          if (/c-hero-banner|c-floating|c-text-contents/.test(cls) || cur.tagName === 'SECTION') {
            // 이 컨테이너 내 AEM bodycopy 우선
            const bodyP = cur.querySelector('[class*="__bodycopy"] .cmp-text p, [class*="bodycopy"] p, .cmp-text p');
            if (bodyP) {
              const t = bodyP.innerText?.trim();
              if (t && t.length > 10 && !t.startsWith('*')) return t;
            }
            // AEM headline
            const hlEl = cur.querySelector('[class*="__headline"] .cmp-title, .cmp-title__text, .cmp-title');
            if (hlEl) {
              const t = hlEl.innerText?.trim();
              if (t && t.length > 2 && t.length < 200) return t;
            }
          }
          cur = cur.parentElement;
        }

        // 1) <figure> > <figcaption>
        const fig = img.closest('figure');
        if (fig) {
          const cap = fig.querySelector('figcaption')?.innerText?.trim();
          if (cap && cap.length > 2) return cap;
        }
        // 2) 같은 컨테이너의 h3/h4/p (이미지 다음 형제 또는 부모 형제)
        const parent = img.parentElement;
        if (parent) {
          // 형제 중 텍스트 요소 (heading 우선)
          const headingSib = Array.from(parent.children).find(sib => {
            if (sib === img) return false;
            const tag = sib.tagName;
            return tag === 'H2' || tag === 'H3' || tag === 'H4';
          });
          if (headingSib) {
            const t = headingSib.innerText?.trim();
            if (t && t.length > 2 && t.length < 200) return t;
          }
          // 형제 중 텍스트 요소
          for (const sib of Array.from(parent.children)) {
            if (sib === img) continue;
            const t = sib.innerText?.trim();
            if (t && t.length > 2 && t.length < 200) return t;
          }
          // 부모의 형제에서 찾기
          const grandP = parent.parentElement;
          if (grandP && grandP !== root) {
            for (const sib of Array.from(grandP.children)) {
              if (sib.contains(img)) continue;
              const el = sib.querySelector('h2,h3,h4,[class*="__headline"],[class*="-title"],[class*="-desc"]');
              const t = el?.innerText?.trim();
              if (t && t.length > 2 && t.length < 200) return t;
            }
          }
        }
        // 3) img alt 텍스트 (마지막 fallback)
        return img.alt?.trim() || '';
      }

      function extractImgs(root) {
        const rawImgs = [];

        // 1) 일반 <img> 태그
        Array.from(root.querySelectorAll('img')).forEach(img => {
          const src = bestSrc(img);
          if (!src) return;
          // naturalWidth ≤ 1은 placeholder 크기 → 실제 이미지 크기가 아니므로 0으로 처리
          // (크기 필터 'width < 150' 오판 방지)
          const isPlaceholderLoaded = img.naturalWidth <= 1;
          const w = isPlaceholderLoaded ? (+img.getAttribute('width') || 0)
                                        : (img.naturalWidth || +img.getAttribute('width') || 0);
          const h = isPlaceholderLoaded ? (+img.getAttribute('height') || 0)
                                        : (img.naturalHeight || +img.getAttribute('height') || 0);
          const nearText = findNearImageText(img, root);
          rawImgs.push({ url: src, width: w, height: h,
                   ar: w > 0 && h > 0 ? +(w/h).toFixed(3) : 0,
                   alt: img.alt || '', nearText });
        });

        // 2) <video poster="..."> 포스터 이미지
        Array.from(root.querySelectorAll('video[poster]')).forEach(v => {
          const poster = v.getAttribute('poster') || '';
          if (poster && !poster.startsWith('data:')) {
            rawImgs.push({ url: poster, width: 0, height: 0, ar: 1.78, alt: 'Video poster', nearText: '' });
          }
        });

        // 3) YouTube / Vimeo iframe 썸네일
        Array.from(root.querySelectorAll('iframe')).forEach(iframe => {
          const src = iframe.getAttribute('src') || iframe.getAttribute('data-src') || '';
          const ytMatch = src.match(/youtube(?:-nocookie)?\.com\/embed\/([^?&/"]+)/);
          const vimeoMatch = src.match(/vimeo\.com\/video\/(\d+)/);
          if (ytMatch) {
            const vid = ytMatch[1];
            rawImgs.push({
              url: `https://img.youtube.com/vi/${vid}/hqdefault.jpg`,
              width: 480, height: 360, ar: 1.33, alt: 'Video', nearText: ''
            });
          } else if (vimeoMatch) {
            // Vimeo는 API가 필요하므로 placeholder URL 사용 (로드 시 대체)
          }
        });

        // 4) data-youtube-id / data-video-id 속성 (커스텀 플레이어)
        Array.from(root.querySelectorAll('[data-youtube-id],[data-video-id],[data-vid]')).forEach(el => {
          const vid = el.dataset.youtubeId || el.dataset.videoId || el.dataset.vid;
          if (vid && /^[a-zA-Z0-9_-]{8,12}$/.test(vid)) {
            rawImgs.push({
              url: `https://img.youtube.com/vi/${vid}/hqdefault.jpg`,
              width: 480, height: 360, ar: 1.33, alt: 'Video', nearText: ''
            });
          }
        });

        // 5) CSS background-image — root 및 모든 하위 요소 스캔 (full-bleed 섹션 대응)
        const bgCandidates = [root, ...Array.from(root.querySelectorAll('*'))];
        bgCandidates.forEach(el => {
          try {
            if (el.offsetWidth < 200 || el.offsetHeight < 80) return; // 너무 작은 요소 제외
            const bg = window.getComputedStyle(el).backgroundImage;
            if (!bg || bg === 'none') return;
            // 여러 레이어 중 첫 url() 추출
            const match = bg.match(/url\(['"]?([^'")\s]+)['"]?\)/);
            if (match) {
              const bgUrl = abs(match[1]);
              if (bgUrl && !bgUrl.startsWith('data:') &&
                  !/icon|logo|\.svg|gradient|pixel|1x1|sprite/.test(bgUrl)) {
                rawImgs.push({
                  url: bgUrl,
                  width: el.offsetWidth,
                  height: el.offsetHeight,
                  ar: el.offsetWidth > 0 && el.offsetHeight > 0
                    ? +(el.offsetWidth / el.offsetHeight).toFixed(3) : 0,
                  alt: el.getAttribute('aria-label') || el.title || '',
                  nearText: ''
                });
              }
            }
          } catch (_) {}
        });

        // 6) 카드 패턴 명시 수집 — h3/h4 + img 반복 구조 (carousel, tab, grid card)
        // 이미 수집된 URL 세트
        const collectedUrls = new Set(rawImgs.map(i => i.url.replace(/[?#].*/, '')));
        const CARD_SELS = [
          '[class*="card"]', '[class*="swiper-slide"]', '[class*="slick-slide"]',
          '[class*="-slide"]', '[class*="-item"]', '[class*="-panel"]',
          '[class*="tab-content"]', 'li',
        ];
        CARD_SELS.forEach(sel => {
          try {
            Array.from(root.querySelectorAll(sel)).forEach(card => {
              if (card.offsetHeight < 50 || card.offsetWidth < 80) return;
              // 카드 내에 heading이 있어야 의미 있는 카드
              if (!card.querySelector('h2,h3,h4,h5,strong,[class*="title"],[class*="tit"],[class*="heading"]')) return;
              const cardImg = card.querySelector('img');
              if (!cardImg) return;
              const src = bestSrc(cardImg);
              if (!src) return;
              const baseUrl = src.replace(/[?#].*/, '');
              if (collectedUrls.has(baseUrl)) return;
              collectedUrls.add(baseUrl);
              const w = cardImg.naturalWidth  || +cardImg.getAttribute('width')  || 0;
              const h = cardImg.naturalHeight || +cardImg.getAttribute('height') || 0;
              const nearText = findNearImageText(cardImg, root);
              rawImgs.push({ url: src, width: w, height: h,
                ar: w > 0 && h > 0 ? +(w/h).toFixed(3) : 0,
                alt: cardImg.alt || '', nearText });
            });
          } catch (_) {}
        });

        // 필터링
        const filtered = rawImgs.filter(i => {
          if (!i.url || i.url.startsWith('data:')) return false;
          const u = i.url.toLowerCase();
          if (/icon|logo|\.svg|blank|placeholder|spinner|pixel|rating|star/.test(u)) return false;
          const filename = u.split('/').pop() || '';
          if (/^loading|[-_]loading[-_.]|loading\.(gif|png|webp)$/.test(filename)) return false;
          // 아이콘 크기 패턴: _24x24.png 같은 경우
          if (/_(\d{1,2})x(\d{1,2})\.(png|jpg|gif|webp)/.test(u)) return false;
          // naturalWidth가 0이면 아직 로딩 전 → URL 패턴이 괜찮으면 허용
          // naturalWidth가 있으면 150px 미만 아이콘 제외
          if (i.width > 0 && i.width < 150) return false;
          // URL에 고해상도 힌트가 있으면 (1600, 1920 등) 명백히 콘텐츠 이미지
          const isHighRes = /[_-](1\d{3}|2\d{3})x/.test(u) || u.includes('/large/') || u.includes('/full/');
          if (isHighRes) return true;
          return true;
        });

        // 중복 제거
        const seen = new Set();
        return filtered.filter(i => {
          const key = i.url.replace(/[?#].*/, '').replace(/-\d{2,4}x\d{2,4}/, '');
          if (seen.has(key)) return false;
          seen.add(key); return true;
        });
      }

      function extractText(root) {
        // ── Eyebrow (AEM: 헤드라인 위의 짧은 카테고리 태그라인) ──
        let eyebrow = '';
        const eyebrowEl = root.querySelector(
          '[class*="__eyebrow"] .cmp-text, [class*="__eyebrow"]');
        if (eyebrowEl) {
          const t = eyebrowEl.innerText?.trim();
          if (t && t.length > 1 && t.length < 100 && !isSkip(t)) eyebrow = t;
        }

        // ── Headline ──
        let hl = '';
        const hlSels = [
          // AEM 전용
          '[class*="__headline"] .cmp-title__text', '[class*="__headline"] .cmp-title',
          '.cmp-title__text', '.cmp-title',
          // 일반
          'h2', 'h3', '[class*="-title"]:not(button)',
          '[class*="-tit"]:not(button)', '[class*="heading"]',
          '.tit', '.title', '.kv-title'
        ];
        for (const sel of hlSels) {
          const el = root.querySelector(sel);
          const t = el?.innerText?.trim();
          if (t && t.length >= 3 && t.length < 200 &&
              !isSkip(t) && !looksLikeClassName(t)) {
            hl = t; break;
          }
        }

        // ── Subheadline ──
        let sub = '';
        for (const sel of ['h3', 'h4', '[class*="sub-title"]', '[class*="subtitle"]', '.sub-tit']) {
          const el = root.querySelector(sel);
          const t = el?.innerText?.trim();
          if (t && t !== hl && t.length >= 3 && t.length < 200 &&
              !looksLikeClassName(t)) { sub = t; break; }
        }

        // ── Body copy ──
        // 1) AEM 전용 bodycopy 셀렉터 우선
        let body = '';
        const aemBodySels = [
          '[class*="__bodycopy"] .cmp-text p',
          '[class*="bodycopy"] .cmp-text p',
          '[class*="__bodycopy"] .cmp-text',
          '[class*="bodycopy"] p',
          '.cmp-text p',
          '.cmp-text',
        ];
        for (const aemSel of aemBodySels) {
          const els = Array.from(root.querySelectorAll(aemSel));
          const texts = els
            .map(el => el.innerText?.trim())
            .filter(t => t && t.length > 20 && t.length < 1000 &&
                        !isSkip(t) && !looksLikeClassName(t) && !t.startsWith('*'));
          if (texts.length > 0) { body = texts.slice(0, 3).join('\n'); break; }
        }

        // 2) AEM bodycopy 없으면 일반 p/desc (depth 제한 완화: 15)
        if (!body) {
          const bodyEls = Array.from(root.querySelectorAll(
              'p, [class*="-desc"], [class*="-body"], [class*="-text"], [class*="description"]'))
            .filter(el => {
              let depth = 0, cur = el;
              while (cur && cur !== root && depth < 16) { cur = cur.parentElement; depth++; }
              return depth < 15;
            });
          body = bodyEls
            .map(el => el.innerText?.trim())
            .filter(t => t && t.length > 20 && t.length < 1000 &&
                        !isSkip(t) && !looksLikeClassName(t) && !t.startsWith('*'))
            .slice(0, 3).join('\n');
        }

        // ── Footnotes (* 로 시작하는 p 태그) → body에 덧붙이기 ──
        const footnotes = Array.from(root.querySelectorAll('p, [class*="footnote"], [class*="disclaimer"]'))
          .map(el => el.innerText?.trim())
          .filter(t => t && t.startsWith('*') && t.length > 10 && t.length < 500)
          .slice(0, 2);
        if (footnotes.length > 0) {
          body = (body ? body + '\n' : '') + footnotes.join('\n');
        }

        // ── Bullets ──
        const bullets = Array.from(root.querySelectorAll('li'))
          .map(el => el.innerText?.trim())
          .filter(t => t && t.length > 3 && t.length < 200 &&
                       !isSkip(t) && !looksLikeNavBullet(t))
          .slice(0, 8);

        // eyebrow는 sub로 활용 (sub 없을 때)
        return { hl, sub: sub || eyebrow, body, bullets };
      }

      // ── 섹션 후보 선정 ────────────────────────────────
      // 헤더/푸터/내비 조상 요소 감지
      function isNavOrFooter(el) {
        let cur = el;
        while (cur && cur !== document.body) {
          const tag = cur.tagName?.toLowerCase();
          if (tag === 'header' || tag === 'footer' || tag === 'nav') return true;
          const cls = (cur.className || '').toLowerCase();
          if (/\b(header|footer|nav|navigation|breadcrumb|sitemap)\b/.test(cls)) return true;
          cur = cur.parentElement;
        }
        return false;
      }

      // 전략 1: LG 전용 클래스 셀렉터 (가장 정확)
      // 중첩 요소 필터 — 리스트 내 다른 요소의 자손인 경우 제거 (래퍼 vs 리프 구분)
      function filterLeafNodes(els) {
        return els.filter(el =>
          els.every(other => other === el || !other.contains(el))
        );
      }

      const SPECIFIC_SELS = [
        // ─── LG SA/GCC/Middle East ───────────────────────────────────────
        '.module-item', '.module-kv', '.module-feature', '[class*="module-item"]',

        // ─── LG Levant / 구형 사이트 ──────────────────────────────────────
        '.iw_component', '.component-wrap', '.feature-area',

        // ─── LG UK/EU AEM: c-floating-contents (feature 섹션 단위) ─────────
        // ⚠️ [class*="c-X"] 와일드카드 최소화:
        //    c-hero-banner → __media, __content 자식도 매칭 → 조기 종료 버그
        //    c-media → .c-media__image 등 매칭 → 동일 문제
        // → 정확한 클래스명(.c-floating-contents)만 사용, 와일드카드는 제거
        '.c-floating-contents',
        '.c-product-feature',
        '.c-info-section',
        '.c-media-carousel__item',

        // ─── LG AEM 공통 teaser ───────────────────────────────────────────
        '.cmp-teaser', '[class*="cmp-teaser"]',
        '.cmp-container > .container', '.aem-container',

        // ─── LG UK/EU 일반 ────────────────────────────────────────────────
        '.pdp-feature-item', '.pdp-feature-section', '.product-feature', '.product-benefit',
        '[class*="feature-item"]', '[class*="feature-block"]', '[class*="feature-section"]',

        // ─── LG US ────────────────────────────────────────────────────────
        '.pdp-feature', '[class*="pdp-feature"]',

        // ─── LG 공통 ──────────────────────────────────────────────────────
        '.kv-area', '.kv-feature', '.highlight__item', '.highlight-item',
        '[class*="highlight"][class*="item"]',
        '[class*="reason"][class*="item"]',
        '[class*="benefit"][class*="item"]',

        // ─── AEM section 단위 ─────────────────────────────────────────────
        '[class*="feature"][class*="section"]',

        // ─── 일반 fallback ─────────────────────────────────────────────────
        '.cont-inner', '.inner-container', '.feature-list__item',
      ];

      let sections = [];

      // Strategy 1: LG 전용 셀렉터 — 이미지가 있는 섹션을 최소 1개 이상 포함해야 채택
      for (const sel of SPECIFIC_SELS) {
        try {
          const raw = Array.from(document.querySelectorAll(sel))
            .filter(el => el.offsetHeight > 80 && el.offsetWidth > 100 && !isNavOrFooter(el));
          const found = filterLeafNodes(raw).filter(el => {
            if (el.offsetHeight < 3000) return true;
            // 캐러셀/탭 컨테이너는 슬라이드 그루핑을 위해 더 큰 높이 허용
            const hasCarousel = el.querySelector(
              '[class*="swiper"],[class*="slick"],[class*="carousel"],[class*="-slide"]'
            );
            return hasCarousel && el.offsetHeight < 8000;
          });
          if (found.length >= 2) {
            // 이미지가 포함된 섹션이 하나 이상 있어야 채택 (텍스트 전용 셀렉터 오매칭 방지)
            const hasImgSection = found.some(el => el.querySelectorAll('img').length > 0 || (() => {
              const bg = window.getComputedStyle(el).backgroundImage;
              return bg && bg !== 'none' && bg.includes('url(');
            })());
            if (hasImgSection) {
              sections = found;
              console.log('[analyze] selector:', sel, found.length);
              break;
            }
          }
        } catch (_) {}
      }

      // 전략 2: iw_section 직계 자식 기반 (LG Levant 구조 대응)
      if (sections.length < 2) {
        const iwRoot = document.querySelector('.iw_viewport-wrapper, .iw_section, [class*="iw_section"]');
        if (iwRoot) {
          const candidates = Array.from(iwRoot.querySelectorAll('.iw_component, .component-wrap > *, div[class*="GPC"]'))
            .filter(el => el.offsetHeight > 100 && el.offsetWidth > 200 &&
                          !isNavOrFooter(el) && el.querySelector('h2,h3'));
          if (candidates.length >= 1) {
            sections = filterLeafNodes(candidates);
            console.log('[analyze] iw-component strategy:', sections.length);
          }
        }
      }

      // 전략 3: 컨텐츠 스코어링 — Strategy 1 결과와 무관하게 항상 보완 실행
      // 이유: Strategy 1이 gram Link 카드(c-floating-contents 클래스 공유)를 먼저 찾아
      //       feature-04~06 같은 핵심 섹션이 누락되는 구조적 문제 방지
      {
        const pageRoot = document.querySelector('main, [role="main"], #main, .main-content, .pdp-main, .iw_viewport-wrapper') || document.body;
        const candidates = Array.from(pageRoot.querySelectorAll(
          'section, article, [class*="section"], [class*="block"], [class*="feature"], [class*="banner"], div[class]'
        )).filter(el =>
          el.offsetHeight > 120 && el.offsetHeight < 4000 &&
          el.offsetWidth > 300 && !isNavOrFooter(el)
        );
        const scored = candidates.map(el => {
          const imgCount = el.querySelectorAll('img').length;
          const hasBgImg = (() => {
            try {
              const bg = window.getComputedStyle(el).backgroundImage;
              return bg && bg !== 'none' && bg.includes('url(') &&
                     el.offsetWidth > 400 && el.offsetHeight > 150;
            } catch (_) { return false; }
          })();
          const hasHl  = !!el.querySelector('h1,h2,h3,h4');
          const hasTxt = (el.innerText?.trim().length || 0) > 30;
          const score  = (imgCount > 0 ? 3 : 0) + (hasBgImg ? 3 : 0) + (hasHl ? 2 : 0) + (hasTxt ? 1 : 0);
          return { el, score };
        }).filter(s => s.score >= 3).sort((a, b) => b.score - a.score);

        if (scored.length >= 2) {
          const scoredSections = filterLeafNodes(scored.map(s => s.el));
          if (sections.length < 2) {
            // Strategy 1/2 실패: Strategy 3을 주 전략으로 사용
            sections = scoredSections;
            console.log('[analyze] content-score primary:', sections.length);
          } else {
            // Strategy 1/2 성공: Strategy 3을 보완으로 사용 (누락된 섹션 추가)
            const existing = new Set(sections);
            const additional = scoredSections.filter(el =>
              !existing.has(el) &&
              // Strategy 1 섹션과 부모-자식 관계가 아닌 것만 추가
              !sections.some(s => s.contains(el) || el.contains(s))
            );
            if (additional.length > 0) {
              sections = [...sections, ...additional];
              console.log('[analyze] content-score supplement:', additional.length, 'added');
            }
          }
        }
      }

      // 전략 4: 페이지 루트 직계 자식 (최후 fallback)
      if (sections.length < 2) {
        const mainEl = document.querySelector('main, [role="main"], #main');
        if (mainEl) {
          sections = Array.from(mainEl.children)
            .filter(el => !['SCRIPT','STYLE','NAV','HEADER'].includes(el.tagName) &&
                          el.offsetHeight > 100 && !isNavOrFooter(el));
          console.log('[analyze] fallback main children:', sections.length);
        }
      }

      // ── 서브섹션 분할 헬퍼 ──────────────────────────────────────────────────
      // 하나의 섹션에 여러 H2 그룹(카드 row, 탭 그룹 등)이 있을 때 분할
      function trySplitSection(sec) {
        const h2list = Array.from(sec.querySelectorAll('h2')).filter(h => {
          const t = h.innerText?.trim() || '';
          return t.length >= 5 && t.length < 300 && !isSkip(t) && !looksLikeClassName(t);
        });
        if (h2list.length < 2) return null;

        // 각 H2를 포함하는 sec의 직접 자식 컨테이너를 찾기
        const seenContainers = new Set();
        const groups = [];
        h2list.forEach(h => {
          let cur = h;
          // sec의 직접 자식까지 올라가기
          while (cur.parentElement && cur.parentElement !== sec) cur = cur.parentElement;
          const container = (cur === sec) ? h.parentElement : cur;
          if (!container || container === sec) return;
          if (seenContainers.has(container)) return;
          seenContainers.add(container);
          groups.push(container);
        });

        // 유효한 그룹 (충분한 콘텐츠) 필터링
        const valid = groups.filter(g =>
          g.offsetHeight > 80 &&
          (g.querySelectorAll('img').length > 0 || (g.innerText?.trim().length || 0) > 40)
        );
        if (valid.length >= 2) return valid;

        // Fallback: sec의 직접 자식 중 heading + (img or 텍스트) 포함하는 블록
        const children = Array.from(sec.children).filter(child =>
          child.offsetHeight > 80 &&
          child.querySelector('h2,h3,h4') &&
          (child.querySelectorAll('img').length > 0 || (child.innerText?.trim().length || 0) > 40)
        );
        if (children.length >= 2) return children;

        return null;
      }

      // ── 카드 그룹 이미지 + 텍스트 추출 헬퍼 ──────────────────────────────
      // 섹션 내 반복 카드(h3/h4+img 패턴)를 모두 모아 items 배열로 반환
      function extractCardItems(sec) {
        // 카드 아이템을 담는 컨테이너 후보 (swiper/slick 포함)
        const CARD_CONTAINER_SELS = [
          // 캐러셀/슬라이더 래퍼 (최우선 — swiper-slide의 직접 부모)
          '[class*="swiper-wrapper"]', '[class*="swiper-container"]',
          '[class*="slick-track"]', '[class*="slick-list"]',
          // 일반 카드 컨테이너
          '[class*="card-list"]', '[class*="cards"]',
          '[class*="tab-content"]', '[class*="slide-content"]',
          '[class*="items"]', '[class*="grid"]', 'ul',
        ];
        // 카드 아이템 후보 (offsetHeight 무조건 체크)
        const CARD_ITEM_SELS = [
          '[class*="swiper-slide"]', '[class*="slick-slide"]',
          '[class*="card"]', '[class*="-slide"]', '[class*="-item"]', 'li',
        ];
        let cards = [];

        // 1) 카드 컨테이너 → 직접 자식 카드 탐색
        for (const cSel of CARD_CONTAINER_SELS) {
          const cont = sec.querySelector(cSel);
          if (!cont) continue;
          for (const iSel of CARD_ITEM_SELS) {
            const items = Array.from(cont.querySelectorAll(':scope > ' + iSel))
              // offsetHeight > 0 (display:block으로 전환된 슬라이드는 높이 있음)
              .filter(el => el.offsetHeight > 0 && el.querySelector('img'));
            if (items.length >= 2) { cards = items; break; }
          }
          if (cards.length >= 2) break;
        }

        // 2) 컨테이너 없으면 섹션 전체에서 비직접 자식까지 탐색
        if (cards.length < 2) {
          for (const iSel of CARD_ITEM_SELS) {
            const items = Array.from(sec.querySelectorAll(iSel))
              .filter(el => el.offsetHeight > 0 && el.querySelector('img'));
            if (items.length >= 2) {
              // 최상위 카드만 남기기 (중첩 카드 제거)
              const topLevel = items.filter(el =>
                items.every(other => other === el || !other.contains(el))
              );
              if (topLevel.length >= 2) { cards = topLevel; break; }
            }
          }
        }

        if (cards.length < 2) return null;

        return cards.map(card => {
          const img = card.querySelector('img');
          const src = img ? bestSrc(img) : '';
          const titleEl = card.querySelector('h3,h4,h5,strong,[class*="title"],[class*="tit"]');
          const bodyEl  = card.querySelector('p,[class*="desc"],[class*="body"],[class*="text"]');
          return {
            imageUrl: src || '',
            title: titleEl?.innerText?.trim() || '',
            body:  bodyEl?.innerText?.trim() || '',
          };
        }).filter(item => item.imageUrl || item.title);
      }

      // ── 섹션 → feature 변환 ────────────────────────────
      const result = [];
      const seenHl  = new Set();
      const seenImg = new Set();
      let featureIdx = 0;

      function processSection(sec) {
        const idx = featureIdx++;
        const { hl, sub, body, bullets } = extractText(sec);

        // 스킵 조건들
        if (isSkip(hl) || isSkip(sub)) return;
        if (looksLikeClassName(hl)) return;
        if (hl && /^[A-Z]{2,}$/.test(hl.trim())) return;
        if (!hl && !body && bullets.length === 0) return;
        if (hl && seenHl.has(hl.toLowerCase())) return;
        if (hl) seenHl.add(hl.toLowerCase());

        // 카드 아이템 수집 (3~4장 카드 패턴 우선)
        const cardItems = extractCardItems(sec);

        const imgs = extractImgs(sec)
          .filter(i => !seenImg.has(i.url.replace(/[?#].*/, '')))
          .slice(0, 6); // 4 → 6으로 증가 (카드 3장+ 지원)
        imgs.forEach(i => seenImg.add(i.url.replace(/[?#].*/, '')));

        if (imgs.length === 0 && !hl && (!body || body.length < 80)) return;
        if (imgs.length === 0 && (!body || body.length < 30) && bullets.length < 2) return;
        if (hl && body && imgs.length === 0) {
          const hlNorm = hl.toLowerCase().replace(/\s+/g, ' ');
          const bodyNorm = body.toLowerCase().replace(/\s+/g, ' ');
          if (bodyNorm.split(hlNorm).length > 2) return;
        }

        let cleanBody = body;
        if (hl && body) {
          const hlNorm = hl.toLowerCase().trim();
          const lines = body.split('\n').filter(line => {
            const l = line.toLowerCase().trim();
            return l !== hlNorm && l.length > 0;
          });
          cleanBody = lines.join('\n').trim();
        }

        const sortedImgs = [...imgs].sort((a, b) => {
          const sa = (a.width || 0) + (a.ar >= 0.5 && a.ar <= 4 ? 1000 : 0);
          const sb = (b.width || 0) + (b.ar >= 0.5 && b.ar <= 4 ? 1000 : 0);
          return sb - sa;
        });

        result.push({
          id: `f${idx}`,
          order: idx,
          headline: hl,
          subheadline: sub,
          body: cleanBody,
          bullets,
          images: sortedImgs,
          // 카드 아이템이 있으면 포함 (three-img/four-text 모듈에 직접 매핑)
          cardItems: cardItems && cardItems.length >= 2 ? cardItems : undefined,
        });
      }

      sections.forEach(sec => {
        // 서브섹션 분할 시도 (H2 그룹이 2개 이상인 경우)
        const subSections = trySplitSection(sec);
        if (subSections) {
          console.log('[analyze] split section →', subSections.length, 'sub-sections');
          subSections.forEach(sub => processSection(sub));
        } else {
          processSection(sec);
        }
      });

      return result;
    });

    console.log(`[analyze] ${url} → ${features.length} features`);
    res.json({ features, url });
  } catch (e) {
    console.error('/api/analyze error:', e);
    res.status(500).json({ error: e.message });
  } finally {
    await browser.close();
  }
});

/* ──────────────────────────────────────────
   이미지 프록시 (CORS 우회)
────────────────────────────────────────── */
app.get('/api/proxy-image', async (req, res) => {
  const imageUrl = req.query.url;
  if (!imageUrl) return res.status(400).send('Missing url param');
  try {
    const https = require('https');
    const http = require('http');
    const urlObj = new URL(imageUrl);
    const protocol = urlObj.protocol === 'https:' ? https : http;
    const request = protocol.get(imageUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://www.lg.com/'
      }
    }, (imgRes) => {
      // 리다이렉트 처리
      if (imgRes.statusCode >= 300 && imgRes.statusCode < 400 && imgRes.headers.location) {
        res.redirect(`/api/proxy-image?url=${encodeURIComponent(imgRes.headers.location)}`);
        return;
      }
      res.set('Access-Control-Allow-Origin', '*');
      res.set('Content-Type', imgRes.headers['content-type'] || 'image/jpeg');
      res.set('Cache-Control', 'public, max-age=3600');
      imgRes.pipe(res);
    });
    request.on('error', (e) => {
      console.error('Proxy error:', e.message);
      res.status(500).send(e.message);
    });
  } catch (e) {
    res.status(500).send(e.message);
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`\n✅ A+ Content Generator Server`);
  console.log(`   http://localhost:${PORT}`);
  console.log(`   API Key: ${process.env.ANTHROPIC_API_KEY ? '✓ loaded' : '✗ missing'}\n`);
});






cd "C:\Users\Administrator\Desktop\AI\RetailOBS\3P\Arc"
node server.js