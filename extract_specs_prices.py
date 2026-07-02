"""SC9S / SH5A / RNC5 스펙 + 가격 추출"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for code in ['SC9S', 'SH5A', 'RNC5']:
    html = open(f'bulk_html/{code}.html', encoding='utf-8', errors='ignore').read()
    print(f'=== {code} ===')

    # Price from various sources
    # 1. JSON-LD
    jlds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    for jld in jlds:
        try:
            d = json.loads(jld)
            if isinstance(d, list): d = d[0]
            if d.get('@type') == 'Product':
                offers = d.get('offers', {})
                if isinstance(offers, list): offers = offers[0]
                p = offers.get('price', '')
                if p: print(f'  Price (JSON-LD): {p} {offers.get("priceCurrency","")}')
                break
        except: pass

    # 2. meta price
    meta_price = re.search(r'"price"\s*:\s*"?(\d[\d,\.]*)"?', html)
    # 3. data-price or ec_price
    ec_price = re.search(r'"ec_price"\s*:\s*"?(\d[\d,\.]*)"?', html)
    if ec_price: print(f'  Price (ec_price): {ec_price.group(1)}')

    # 4. SAR pattern in page
    sar_prices = re.findall(r'SAR\s*([\d,]+\.?\d*)', html)
    sar_prices = [p for p in sar_prices if p.strip() and p.replace(',','').replace('.','').isdigit()]
    if sar_prices:
        sar_set = sorted(set(sar_prices), key=lambda x: float(x.replace(',','')))
        print(f'  SAR prices found: {sar_set[:5]}')

    # c-compare-selling specs (select best 20 for SC9S, all for others)
    spec_pairs = re.findall(
        r'c-compare-selling__spec-name"><p>(.*?)</p>.*?c-compare-selling__spec-desc"><p>(.*?)</p>',
        html, re.S)

    if spec_pairs:
        print(f'  Specs ({len(spec_pairs)} total):')
        # Unique keys only
        seen = set()
        for k, v in spec_pairs:
            k2 = k.strip(); v2 = v.strip()
            if k2 not in seen:
                seen.add(k2)
                print(f'    {k2}: {v2[:70]}')
    else:
        print('  No c-compare-selling specs')
    print()
