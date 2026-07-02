"""SC9S / SH5A / RNC5 갤러리 경로 probe"""
import urllib.request, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
CDN = 'https://www.lg.com/content/dam/channel/wcms/sa_en'

def head_ok(path):
    try:
        req = urllib.request.Request(CDN + path, method='HEAD', headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status == 200
    except:
        return False

# === SC9S: probe large01~15 in various folders ===
print('=== SC9S gallery probe ===')
# bv-product-id = MD07575328
sc9s_gal_bases = [
    '/images/sound-bars/sc9s_dsauelk_emsj_sa_en_c/gallery/',
    '/images/sound-bars/md07575328/gallery/',
    '/images/sound-bars/sc9s/gallery/',
    '/images/speakers/sc9s/gallery/',
    '/images/speakers/md07575328/gallery/',
]
for base in sc9s_gal_bases:
    ok = head_ok(base + 'large01.jpg')
    print(f'  {"OK" if ok else "--"} {base}large01.jpg')
    if ok:
        # Count how many large images exist
        found = []
        for i in range(1, 20):
            p = base + f'large{str(i).zfill(2)}.jpg'
            if head_ok(p):
                found.append(p)
            else:
                break
        print(f'  => found {len(found)} large images: {[p.split("/")[-1] for p in found]}')
        break
    time.sleep(0.2)

# Also check what other gallery files exist in the known folder
print('\n  Known folder scan (first 15 by D-/Z-/DZ- pattern):')
known_base = '/images/sound-bars/sc9s_dsauelk_emsj_sa_en_c/gallery/'
for pat in ['large01.jpg','large02.jpg','large05.jpg','large10.jpg','large15.jpg',
            'D-01.jpg','DZ-01.jpg','Z-01.jpg','2010.jpg','N01_medium01.jpg']:
    ok = head_ok(known_base + pat)
    print(f'  {"OK" if ok else "--"} {pat}')
    time.sleep(0.15)

# === SH5A: probe zoom/gallery pattern ===
print('\n=== SH5A gallery probe ===')
sh5a_base = '/speakers/soundbars/sh5a/'
sh5a_cands = [
    'soundbar-sh5a-2025-gallery-basic.jpg',
    'soundbar-sh5a-2025-gallery-zoom-01.jpg',
    'soundbar-sh5a-2025-gallery-zoom-02.jpg',
    'soundbar-sh5a-2025-gallery-zoom-03.jpg',
    'soundbar-sh5a-2025-gallery-zoom-04.jpg',
    'soundbar-sh5a-2025-gallery-zoom-05.jpg',
    'soundbar-sh5a-2025-gallery-zoom-06.jpg',
    'soundbar-sh5a-2025-gallery-zoom-07.jpg',
    'soundbar-sh5a-2025-gallery-zoom-08.jpg',
    'soundbar-sh5a-2025-gallery-zoom-09.jpg',
    'soundbar-sh5a-2025-gallery-zoom-10.jpg',
]
sh5a_gal_ok = []
for f in sh5a_cands:
    ok = head_ok(sh5a_base + f)
    print(f'  {"OK" if ok else "--"} {f}')
    if ok: sh5a_gal_ok.append(sh5a_base + f)
    time.sleep(0.15)
print(f'  => SH5A gallery: {len(sh5a_gal_ok)} images')

# Also probe /gallery/large01~15 for sh5a
print('  Standard large probe:')
for base in ['/images/sound-bars/sh5a/gallery/', '/images/sound-bars/md08731750/gallery/']:
    ok = head_ok(base + 'large01.jpg')
    print(f'  {"OK" if ok else "--"} {base}large01.jpg')
    time.sleep(0.2)

# SH5A features
print('\n  SH5A feature probe:')
feat_base = '/speakers/soundbars/features/'
for i in range(1, 12):
    p = feat_base + f'soundbar-sh5a-2025-feature-desktop-{str(i).zfill(2)}.jpg'
    ok = head_ok(p)
    print(f'  {"OK" if ok else "--"} {p.split("/")[-1]}')
    time.sleep(0.15)

# === RNC5: probe DZ pattern ===
print('\n=== RNC5 gallery probe ===')
rnc5_base = '/images/sound-bars/rnc5_dsauelk_emsj_sa_en_c/gallery/'
# Check what's in the gallery folder
for pat in ['Basic-450.jpg','D-01.jpg','Z-01.jpg','DZ-01.jpg','DZ-02.jpg','DZ-03.jpg',
            'DZ-04.jpg','DZ-05.jpg','DZ-06.jpg','DZ-07.jpg','DZ-08.jpg',
            'large01.jpg','large02.jpg']:
    ok = head_ok(rnc5_base + pat)
    print(f'  {"OK" if ok else "--"} {pat}')
    time.sleep(0.15)

print('\n  RNC5 features /images/av/features/:')
feat_b = '/images/av/features/'
for f in [
    'AV-XBOOM-RNC5-01-Identity-Desktop.jpg',
    'AV-XBOOM-RNC5-02-DoubleSuperBassBoost-Desktop.jpg',
    'AV-XBOOM-RNC5-03-MultiColorLighting-Thumbnail-Desktop.jpg',
    'AV-XBOOM-RNC5-06-DJapp-Desktop.jpg',
    'AV-XBOOM-RNC5-07-Karaokestar-Desktop.jpg',
    'AV-XBOOM-RNC5-08-Party-Saver-Desktop.jpg',
]:
    ok = head_ok(feat_b + f)
    print(f'  {"OK" if ok else "--"} {f}')
    time.sleep(0.15)
