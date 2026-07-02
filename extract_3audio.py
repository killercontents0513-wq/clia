"""SC9S / SH5A / RNC5 페이지 데이터 추출"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for code in ['SC9S', 'SH5A', 'RNC5']:
    html = open(f'bulk_html/{code}.html', encoding='utf-8', errors='ignore').read()
    print(f'=== {code} ===')

    # data-bv-product-id
    bv = re.search(r'data-bv-product-id=["\']([^"\']+)["\']', html)
    print(f'  bv-product-id: {bv.group(1) if bv else "NOT FOUND"}')

    # canonical URL
    canon = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    print(f'  canonical: {canon.group(1) if canon else "?"}')

    # JSON-LD product info
    jlds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    for jld in jlds:
        try:
            d = json.loads(jld)
            if isinstance(d, list): d = d[0]
            if d.get('@type') == 'Product':
                print(f'  name: {d.get("name","")}')
                offers = d.get('offers', {})
                if isinstance(offers, list): offers = offers[0]
                price = offers.get('price', '')
                if isinstance(price, float) and price == int(price):
                    price = int(price)
                print(f'  price: {price} {offers.get("priceCurrency","")}')
                specs = d.get('additionalProperty', [])
                print(f'  specs in JSON-LD: {len(specs)}')
                if specs:
                    for sp in specs[:5]:
                        print(f'    {sp.get("name","")} = {sp.get("value","")}')
                break
        except Exception as e:
            pass

    # c-compare-selling specs (rendered HTML)
    spec_pairs = re.findall(
        r'c-compare-selling__spec-name"><p>(.*?)</p>.*?c-compare-selling__spec-desc"><p>(.*?)</p>',
        html, re.S)
    print(f'  c-compare-selling specs: {len(spec_pairs)}')
    for k, v in spec_pairs[:8]:
        print(f'    {k.strip()}: {v.strip()}')

    # Key Features
    kf_block = re.search(r'id="keyFeatureList"(.*?)</ul>', html, re.S)
    if kf_block:
        kf_items = re.findall(r'<li[^>]*>(.*?)</li>', kf_block.group(1), re.S)
        kf_clean = [re.sub(r'<[^>]+>', '', x).strip() for x in kf_items if x.strip()]
        print(f'  Key Features ({len(kf_clean)}): {kf_clean}')

    # CDN images
    imgs = re.findall(r'/content/dam/channel/wcms/sa_en(/[^\s"\'<>]+?\.(?:jpg|jpeg|png|webp))', html)
    EXCLUDE = ['/renditions/', '/jcr:content/', 'gnb', 'home-page', 'banners-20',
               'ai-core-tech', 'common-icon', 'members-offer', 'ai-homepage',
               'about-us', 'lg-store', 'tv-', 'refrigerator', 'washing']
    imgs = [i for i in imgs if not any(x in i for x in EXCLUDE)]
    imgs = list(dict.fromkeys(imgs))

    code_l = code.lower()
    gal_cands = [i for i in imgs if '/gallery/' in i]
    feat_cands = [i for i in imgs if code_l in i.lower() and '/gallery/' not in i]
    other = [i for i in imgs if code_l not in i.lower() and '/gallery/' not in i]

    print(f'  Gallery folder: {len(gal_cands)}')
    for g in gal_cands[:5]: print(f'    {g}')
    print(f'  Feature (code match): {len(feat_cands)}')
    for f in feat_cands[:10]: print(f'    {f}')
    print(f'  Other images: {len(other)} (first 5):')
    for o in other[:5]: print(f'    {o}')
    print()
