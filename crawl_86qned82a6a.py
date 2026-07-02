import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

CODE = '86QNED82A6A'
with open(f'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/bulk_html/{CODE}.html', 'r', encoding='utf-8') as f:
    html = f.read()

# --- Price ---
pr_val = ''
jld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
for j in jld:
    try:
        d = json.loads(j.strip())
        if isinstance(d, dict) and d.get('@type') == 'Product':
            offers = d.get('offers', {})
            if isinstance(offers, list): offers = offers[0]
            p = offers.get('price', '')
            if p:
                pf = float(p)
                pr_val = str(int(round(pf)))
    except:
        pass
if not pr_val:
    m = re.search(r'"price"\s*:\s*"?(\d[\d,.]+)"?', html)
    if m: pr_val = m.group(1)
print(f'Price: SAR {pr_val}')

# --- Name ---
m = re.search(r'property=["\']og:title["\']\s+content="([^"]+)"', html)
nm = m.group(1).split(' - ')[0].strip() if m else '86" QNED AI QNED82 4K Smart TV | AI Magic Remote | HDR10 | webOS25'
print(f'Name: {nm}')

# --- Alt helper ---
def get_alt(p):
    fname = p.split('/')[-1]
    idx = html.find(fname)
    if idx == -1:
        return ''
    snip = html[max(0, idx-400):idx+300]
    m = re.search(r'alt="([^"]{3,}?)"', snip)
    return m.group(1) if m else ''

# --- Gallery ---
gal_raw = [
    'images/tvs/qned82/gallery/86qned82a6a/86QNED82A6A-dz-01.jpg',
    'images/tvs/qned82/gallery/86qned82a6a/86QNED82A6A-S-01.jpg',
    'images/tvs/qned82/gallery/86qned82a6a/86QNED82A6A-mz-01.jpg',
    'images/tvs/qned82/gallery/qned-qned82-2025-86-gallery-03.jpg',
    'images/tvs/qned82/gallery/qned-qned82-2025-86-gallery-04.jpg',
    'images/tvs/qned82/gallery/qned-qned82-2025-86-gallery-05.jpg',
    'images/tvs/qned82/gallery/qned-qned80-2025-86-gallery-06.jpg',
    'images/tvs/qned82/gallery/qned-qned82-2025-86-gallery-07.jpg',
    'images/tvs/qned82/gallery/qned-qned82-2025-86-gallery-08.jpg',
    'images/tvs/qned82/gallery/qned-qned82-2025-86-gallery-09.jpg',
    'images/tvs/qned82/gallery/qned-qned82-2025-86-gallery-10.jpg',
    'images/tvs/qned82/gallery/qned-qned82-2025-86-gallery-11-01.jpg',
    'images/tvs/qned82/gallery/qned-qned82-2025-86-gallery-12-01.jpg',
    'images/tvs/qned82/gallery/qned-qned82-2025-86-gallery-13.jpg',
    'images/tvs/qned82/gallery/qned-qned82-2025-86-gallery-14-01.jpg',
    'images/tvs/qned82/gallery/86qned82a6a/2010-15.jpg',
]

defaults = [
    'LG 86" QNED82 4K Smart TV — Front View',
    'LG 86" QNED82 4K Smart TV — Front View',
    'LG 86" QNED82 4K Smart TV — Side View',
    'LG QNED82 TV — Rear View',
    'LG QNED82 TV — Left Side View',
    'LG QNED82 TV — Slim Profile View',
    'LG QNED82 TV — Stand View',
    'LG QNED82 — α7 AI Processor Gen8',
    'LG QNED82 TV — Gallery 08',
    'LG QNED82 TV — Gallery 09',
    'LG QNED82 TV — Gallery 10',
    'LG QNED82 TV — Gallery 11',
    'LG QNED82 TV — Gallery 12',
    'LG QNED82 TV — Gallery 13',
    'LG QNED82 TV — Gallery 14',
    'LG QNED82 TV — Family Wall Mount',
]

print('\n--- Gallery ---')
gal_data = []
for i, p in enumerate(gal_raw):
    a = get_alt(p)
    if not a:
        a = defaults[i] if i < len(defaults) else f'LG 86" QNED82 4K Smart TV — View {i+1}'
    gal_data.append({'p': '/' + p, 'a': a})
    print(f'  {p.split("/")[-1]}: {a[:65]}')

# --- Features (desktop only) ---
feat_raw = [
    '2025_ms_lg-com/tv/qned/qned82/gp1/features/desktop/qned-qned82-2025-00-feature-award-d-1.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-01-feature-kv-d.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-02-feature-dynamic-qned-color-d.jpg',
    'images/tvs/qned82/features/qned-qned80-2025-02-feature-certification-d.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-03-feature-ai-processor-d.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-04-feature-4k-super-upscaling-d.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-05-feature-advanced-local-dimming-d.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-06-feature-ai-magic-remote-d-01.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-07-feature-ai-voice-id-d-01.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-08-feature-ai-search-d.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-09-feature-ai-chatbot-d.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-10-feature-ai-concierge-d-01.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-11-feature-ai-picture-wizard-d.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-12-feature-ai-sound-wizard-d.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-13-feature-webos-re-new-program-d.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-14-feature-ultra-big-tv-d.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-15-feature-ultra-slim-design-d-1.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-15-feature-ultra-slim-design-d-2.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-16-feature-ai-sound-pro-d-1.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-16-feature-ai-sound-pro-d-2.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-16-feature-ai-sound-pro-d-3.jpg',
    '2025_ms_lg-com/tv/qned/qned80/gp1/features/desktop/qned-qned80-2025-17-feature-wow-synergy-d-1.jpg',
    '2025_ms_lg-com/tv/qned/qned80/gp1/features/desktop/qned-qned80-2025-17-feature-wow-synergy-d-2.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-18-feature-powerful-gameplay-d.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-19-feature-best-qned-tv-for-movies-d-01.jpg',
    'images/tvs/qned82/features/qned-qned82-2025-26-feature-resource-efficiency-banner-d.jpg',
]

feat_titles_map = {
    'award':                    ('iF Design Award Winner',          'iF Design Award — 2025 Winner'),
    'kv-d':                     ('LG QNED82 4K Smart TV',           'LG QNED AI 4K Smart TV — QNED82'),
    'dynamic-qned-color':       ('Dynamic QNED Color',              'Dynamic QNED Color — Vivid, True-to-Life'),
    'certification':            ('100% Color Volume DCI-P3',        'Certified 100% Color Volume to DCI-P3'),
    'ai-processor':             ('α7 AI Processor 4K Gen8',         'α7 AI Processor 4K Gen8 — Intelligent Performance'),
    '4k-super-upscaling':       ('4K Super Upscaling',              '4K Super Upscaling — Every Scene, Enhanced'),
    'advanced-local-dimming':   ('Advanced Local Dimming',          'Advanced Local Dimming — Deeper Blacks'),
    'ai-magic-remote':          ('AI Magic Remote',                 'AI Magic Remote — Built-In, Intuitive'),
    'ai-voice-id':              ('AI Voice ID',                     'AI Voice ID — Personalized for You'),
    'ai-search':                ('AI Search',                       'AI Search — Find Anything Instantly'),
    'ai-chatbot':               ('AI Chatbot',                      'AI Chatbot — Conversational Smart TV'),
    'ai-concierge':             ('AI Concierge',                    'AI Concierge — Proactive Recommendations'),
    'ai-picture-wizard':        ('AI Picture Wizard',               'AI Picture Wizard — Optimized Picture'),
    'ai-sound-wizard':          ('AI Sound Wizard',                 'AI Sound Wizard — Auto-Tuned Audio'),
    'webos-re-new':             ('webOS Re:New Program',            'webOS Re:New — Stay Up to Date'),
    'ultra-big-tv':             ('Ultra Big TV Experience',         'Ultra Big TV — Immersive 86" Viewing'),
    'ultra-slim-design':        ('Ultra Slim Design',               'Ultra Slim Design — Sleek & Modern'),
    'ai-sound-pro':             ('AI Sound Pro',                    'AI Sound Pro — Virtual 9.1.2 Up-mix'),
    'wow-synergy':              ('WOW Synergy',                     'WOW Synergy — LG Ecosystem Connected'),
    'powerful-gameplay':        ('Powerful Gameplay',               'Game Optimizer — Powerful Gameplay Mode'),
    'best-qned-tv-for-movies':  ('Best QNED TV for Movies',         'Best QNED TV for Movies — Cinematic'),
    'resource-efficiency':      ('Resource Efficiency',             'Eco-Friendly Design — Resource Efficiency'),
}

print('\n--- Features ---')
feat_data = []
for p in feat_raw:
    a = get_alt(p)
    fname = p.split('/')[-1]
    t = ''
    for key, (alt_fb, title_fb) in feat_titles_map.items():
        if key in p:
            if not a:
                a = alt_fb
            t = title_fb
            break
    if not a:
        a = fname.replace('-', ' ').replace('_', ' ').replace('.jpg', '').title()
    feat_data.append({'p': '/' + p, 'a': a, 't': t, 'd': ''})
    print(f'  {fname[:55]}')
    print(f'    t: {t[:65]}')

# --- Specs ---
raw1 = re.findall(
    r'c-compare-selling__spec-name[^>]*>.*?<p[^>]*>(.*?)</p>.*?c-compare-selling__spec-desc[^>]*>.*?<p[^>]*>(.*?)</p>',
    html, re.DOTALL)
specs = {}
for k, v in raw1:
    k2 = re.sub(r'<[^>]+>', '', k).strip()
    v2 = re.sub(r'<[^>]+>', '', v).strip()
    if k2 and v2:
        specs[re.sub(r'[^\w]', '_', k2).strip('_')] = v2
print(f'\nSpecs: {len(specs)}')

# Save
data = {'nm': nm, 'pr': pr_val, 'gal': gal_data, 'feat': feat_data, 'sp': specs}
out = 'C:/Users/Administrator/Desktop/AI/RetailOBS/3P/86qned82a6a_data.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'Saved: gal={len(gal_data)}, feat={len(feat_data)}, sp={len(specs)}')
