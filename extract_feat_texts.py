"""SC9S / SH5A / RNC5 피처 텍스트 추출"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_feat_text(html, stem, context=4000):
    """파일명 stem 주변에서 제목/설명 추출"""
    pos = html.lower().find(stem.lower())
    if pos < 0:
        return None, None
    snip = html[max(0, pos-context):pos+500]

    # c-text-contents__headline
    head = re.findall(r'c-text-contents__headline[^>]*>(?:<[^>]+>)*([^<]{5,200})', snip)
    body = re.findall(r'c-text-contents__body[^>]*>(?:<[^>]+>)*([^<]{10,500})', snip)

    # Also look for h2, h3 tags
    if not head:
        head = re.findall(r'<h[23][^>]*>(?:<[^>]+>)*([^<]{5,120})</h[23]>', snip, re.S)
    # p tags near feature
    if not body:
        body = re.findall(r'<p[^>]*class[^>]*body[^>]*>([^<]{10,300})</p>', snip)

    title = re.sub(r'\s+', ' ', head[-1]).strip() if head else ''
    desc  = re.sub(r'\s+', ' ', body[-1]).strip() if body else ''
    return title, desc

# ========== SC9S ==========
print('=== SC9S ===')
html = open('bulk_html/SC9S.html', encoding='utf-8', errors='ignore').read()

sc9s_feats = [
    # (stem, fallback_alt, fallback_title, fallback_desc)
    ('AV-SoundBar-SC9S-02-3-Synergy-Desktop',     'WOW Orchestra',    'WOW Orchestra — Synchronized TV & Soundbar Sound', 'WOW Orchestra syncs your LG TV and soundbar for optimized, immersive audio output.'),
    ('AV-SoundBar-SC9S-03-3-Advanced-Sound',       'Advanced Sound',   'Advanced Sound Experience — Dolby Atmos & DTS:X', 'Triple up-firing channels deliver true Dolby Atmos 3D sound from above for a cinema-at-home experience.'),
    ('soundbar-sc9s-2023-03-1-advanced-sound',     'AI Sound Pro',     'AI Sound Pro — Intelligent Audio Optimization',   'AI Sound Pro analyzes content in real time and automatically adjusts audio settings for the best sound.'),
    ('AV-SoundBar-SC9S-05-4-Smart-Function',       'Smart Function',   'WOW Interface & 4K Pass-Through for Seamless Setup', 'WOW Interface simplifies your home theater setup, and 4K Pass-Through with VRR/ALLM supports gaming.'),
    ('AV-SoundBar-SC9S-05-6-Smart-Function',       'WOW Bracket',      'WOW Bracket — Perfect Match for LG OLED C Series', 'The WOW Bracket cable management system mounts seamlessly with LG OLED C Series TVs.'),
    ('AV-SoundBar-SC9S-05-8-Smart-Function',       'Spatial Sound',    'Triple Level Spatial Sound for Deeper Immersion',  'Triple up-firing drivers create three levels of spatial sound, filling the room with realistic 3D audio.'),
]

feat_paths = {
    'AV-SoundBar-SC9S-02-3-Synergy-Desktop':       '/tvs-soundbars/soundbars/av-soundbar-sc9s-features-2023/desktop/AV-SoundBar-SC9S-02-3-Synergy-Desktop.jpg',
    'AV-SoundBar-SC9S-03-3-Advanced-Sound':        '/images/av/features/D10_AV-SoundBar-SC9S-03-3-Advanced-Sound-Experience-Desktop.jpg',
    'soundbar-sc9s-2023-03-1-advanced-sound':      '/feature/soundbar-sc9s-2023-03-1-advanced-sound-experience-desktop.jpg',
    'AV-SoundBar-SC9S-05-4-Smart-Function':        '/images/av/features/D21_AV-SoundBar-SC9S-05-4-Smart-Function-Desktop.jpg',
    'AV-SoundBar-SC9S-05-6-Smart-Function':        '/images/av/features/D22_AV-SoundBar-SC9S-05-6-Smart-Function-Desktop.jpg',
    'AV-SoundBar-SC9S-05-8-Smart-Function':        '/images/av/features/D24_AV-SoundBar-SC9S-05-8-Smart-Function-Desktop.jpg',
}

for stem, alt, fb_t, fb_d in sc9s_feats:
    t, d = extract_feat_text(html, stem)
    print(f'  [{stem[:40]}]')
    print(f'    title: {t or fb_t}')
    print(f'    desc:  {(d or fb_d)[:100]}')

# ========== SH5A ==========
print('\n=== SH5A ===')
html = open('bulk_html/SH5A.html', encoding='utf-8', errors='ignore').read()

# SH5A feature images: soundbar-sh5a-2025-feature-desktop-01~09
# Extract text for each
for i in range(1, 10):
    stem = f'soundbar-sh5a-2025-feature-desktop-{str(i).zfill(2)}'
    t, d = extract_feat_text(html, stem)
    print(f'  Feature {i:02d}: title={t!r} | desc={d!r}')

# Also check key features
kf_block = re.search(r'id="keyFeatureList"(.*?)</ul>', html, re.S)
if kf_block:
    kf_items = re.findall(r'<li[^>]*>(.*?)</li>', kf_block.group(1), re.S)
    kf_clean = [re.sub(r'<[^>]+>', '', x).strip() for x in kf_items if x.strip()]
    print(f'  Key Features: {kf_clean}')

# Also check spec pairs
specs = re.findall(
    r'c-compare-selling__spec-name"><p>(.*?)</p>.*?c-compare-selling__spec-desc"><p>(.*?)</p>',
    html, re.S)
if specs:
    print(f'  Specs from page: {len(specs)}')
    for k,v in specs[:5]: print(f'    {k.strip()}: {v.strip()[:60]}')

# Check price from JSON-LD
import json
jlds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
for jld in jlds:
    try:
        d2 = json.loads(jld)
        if isinstance(d2, list): d2 = d2[0]
        if d2.get('@type') == 'Product':
            offers = d2.get('offers', {})
            if isinstance(offers, list): offers = offers[0]
            print(f'  Price: {offers.get("price","")} {offers.get("priceCurrency","")}')
            break
    except: pass

# ========== RNC5 ==========
print('\n=== RNC5 ===')
html = open('bulk_html/RNC5.html', encoding='utf-8', errors='ignore').read()

rnc5_feat_stems = [
    'AV-XBOOM-RNC5-01-Identity-Desktop',
    'AV-XBOOM-RNC5-02-DoubleSuperBassBoost-Desktop',
    'AV-XBOOM-RNC5-03-MultiColorLighting-Thumbnail-Desktop',
    'AV-XBOOM-RNC5-06-DJapp-Desktop',
    'AV-XBOOM-RNC5-07-Karaokestar-Desktop',
    'AV-XBOOM-RNC5-08-Party-Saver-Desktop',
]
for stem in rnc5_feat_stems:
    t, d = extract_feat_text(html, stem)
    print(f'  [{stem[14:50]}]')
    print(f'    title: {t!r}')
    print(f'    desc:  {d!r}')

# SC9S price
print('\n=== Prices ===')
for code in ['SC9S','SH5A','RNC5']:
    html2 = open(f'bulk_html/{code}.html', encoding='utf-8', errors='ignore').read()
    jlds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html2, re.S)
    for jld in jlds:
        try:
            d3 = json.loads(jld)
            if isinstance(d3, list): d3 = d3[0]
            if d3.get('@type') == 'Product':
                offers = d3.get('offers', {})
                if isinstance(offers, list): offers = offers[0]
                p = offers.get('price','')
                if isinstance(p, float) and p == int(p): p = int(p)
                print(f'  {code}: {p} {offers.get("priceCurrency","")}')
                break
        except: pass
