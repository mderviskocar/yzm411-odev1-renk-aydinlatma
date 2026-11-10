"""YZM411 Ödev 1. Çalıştırma: python deney.py (proje kökünden).

Giriş: veri/orijinaller/*.jpg, tahminler.json, kimlik.json.
Sıra: tahminleri kaydet -> veri oku -> H1 -> H2 -> H3 -> H4 -> rapor.
Analizler kaynak piksel değerlerinde yapılır; geometrik dönüşüm yalnız
ilk fotoğrafı 90 derece sola çevirmek ve kâğıt noktalarını eşlemek içindir.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import importlib.metadata
import json
import sys

import cv2
import numpy as np
from PIL import Image, ExifTags
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'sonuclar'
LABELS = {'normal': 'Normal ışık', 'golge': 'Gölge', 'lamba': 'Lamba'}
FILES = {'normal': '01_normal.jpg', 'golge': '02_golge.jpg', 'lamba': '03_lamba.jpg'}
# Normal görüntüde, etiket ve yansımadan uzaktaki sarı şişe bölgesi.
ROI = [45, 300, 105, 420]  # x0,y0,x1,y1; yalnız normal fotoğraftan seçildi.
POINTS = np.float32([[600, 670], [700, 720], [850, 850]])
TEXT_CROP = [415, 380, 975, 620]  # 560 x 240; her iki kenarı 4'e tam bölünür.


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(name, rows):
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_rgb(path):
    # imdecode / tofile, Windows'ta Türkçe dosya yollarıyla da çalışır.
    bgr = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError(f'Görüntü okunamadı: {path}')
    return bgr, cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def save_rgb(name, rgb):
    cv2.imencode('.png', cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))[1].tofile(OUT / name)


def brightness(rgb, b=40):
    """uint8 taşmasını önlemek için önce float'a geçilir."""
    return np.clip(rgb.astype(np.float64) + b, 0, 255)


def gamma_transform(rgb, gamma):
    """Gamma formüldeki üstür; 1/gamma kullanılmaz."""
    return np.clip(255.0 * (rgb.astype(np.float64) / 255.0) ** gamma, 0, 255)


def display_uint8(values):
    return np.rint(np.clip(values, 0, 255)).astype(np.uint8)


def corresponding_points(images):
    """Kâğıt düzlemindeki SIFT eşleşmeleriyle fiziksel noktaları yaklaşık izle.

    Homografi fotoğraflara uygulanmaz; yalnız üç koordinat taşınır. Yuvarlanan
    noktalar tam fiziksel eşitlik garantisi taşımaz. Bu, çekimdeki hareketi
    düzeltmiş veya ışığı tek değişken yapmış sayılmaz.
    """
    cv2.setRNGSeed(411)
    normal = cv2.cvtColor(images['normal'], cv2.COLOR_RGB2GRAY)
    region = np.zeros(normal.shape, np.uint8)
    cv2.fillPoly(region, [np.int32([[380, 100], [950, 30], [1110, 1010], [430, 1000]])], 255)
    sift = cv2.SIFT_create(nfeatures=6000)
    key_ref, desc_ref = sift.detectAndCompute(normal, region)
    coords = {'normal': np.rint(POINTS).astype(int)}
    diagnostics = {}
    for key in ('golge', 'lamba'):
        gray = cv2.cvtColor(images[key], cv2.COLOR_RGB2GRAY)
        key_dst, desc_dst = sift.detectAndCompute(gray, None)
        pairs = cv2.BFMatcher().knnMatch(desc_ref, desc_dst, k=2)
        good = [a for pair in pairs if len(pair) == 2 for a, b in [pair] if a.distance < 0.72 * b.distance]
        src = np.float32([key_ref[m.queryIdx].pt for m in good])
        dst = np.float32([key_dst[m.trainIdx].pt for m in good])
        if len(good) < 12:
            raise ValueError(f'{key}: fiziksel nokta eşlemesi için yeterli eşleşme yok')
        h, inliers = cv2.findHomography(src, dst, cv2.RANSAC, 3.0)
        if h is None or int(inliers.sum()) < 12:
            raise ValueError(f'{key}: güvenilir kâğıt homografisi bulunamadı')
        projected = cv2.perspectiveTransform(src.reshape(-1, 1, 2), h).reshape(-1, 2)
        errors = np.linalg.norm(projected - dst, axis=1)[inliers.ravel().astype(bool)]
        coords[key] = np.rint(cv2.perspectiveTransform(POINTS.reshape(-1, 1, 2), h).reshape(-1, 2)).astype(int)
        diagnostics[key] = {'eslesme': len(good), 'inlier': int(inliers.sum()),
                            'medyan_hata_px': float(np.median(errors)), 'H': h.tolist()}
    return coords, diagnostics


def make_panel(images, titles, output, columns, width=12):
    rows = (len(images) + columns - 1) // columns
    fig, axes = plt.subplots(rows, columns, figsize=(width, rows * 3.2), squeeze=False)
    for ax in axes.ravel():
        ax.axis('off')
    for ax, image, title in zip(axes.ravel(), images, titles):
        ax.imshow(image, cmap='gray' if image.ndim == 2 else None, vmin=0, vmax=255)
        ax.set_title(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / output, dpi=170, facecolor='white')
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    (ROOT / 'veri/islenmis').mkdir(parents=True, exist_ok=True)
    predictions = json.loads((ROOT / 'tahminler.json').read_text(encoding='utf-8'))
    prediction_path = OUT / 'tahmin_kaydi.json'
    prediction_hash = sha256(ROOT / 'tahminler.json')
    if prediction_path.exists():
        prior = json.loads(prediction_path.read_text(encoding='utf-8'))
        if prior['sha256'] != prediction_hash:
            raise ValueError('İlk deneyden sonra tahminler değişmiş; yeni deney sürümü açıkça oluşturulmalı.')
    else:
        # Bu kayıt herhangi bir deney ölçümünden önce diske yazılır.
        write_json(prediction_path, {'ilk_deney_oncesi_utc': datetime.now(timezone.utc).isoformat(),
                                    'sha256': prediction_hash, 'tahminler': predictions})
    images, metadata, source_hashes = {}, [], {}
    for key, filename in FILES.items():
        path = ROOT / 'veri/orijinaller' / filename
        bgr, rgb = read_rgb(path)
        source_hashes[filename] = sha256(path)
        if key == 'normal':
            rgb = cv2.rotate(rgb, cv2.ROTATE_90_COUNTERCLOCKWISE)
            encoded = cv2.imencode('.png', cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))[1]
            encoded.tofile(ROOT / 'veri/islenmis/normal_isik_90sol.png')
        images[key] = rgb
        with Image.open(path) as image:
            exif = image.getexif()
            try:
                nested = exif.get_ifd(0x8769)
            except (KeyError, TypeError):
                nested = {}
            useful = {ExifTags.TAGS.get(k, str(k)): str(v) for k, v in {**dict(exif), **nested}.items()
                      if ExifTags.TAGS.get(k, '') in ['Make', 'Model', 'DateTimeOriginal', 'ExposureTime',
                                                     'ISOSpeedRatings', 'WhiteBalance', 'ExposureMode', 'Software']}
        metadata.append({'kosul': key, 'H': rgb.shape[0], 'W': rgb.shape[1], 'C': rgb.shape[2],
                         'dtype': str(rgb.dtype), 'min': int(rgb.min()), 'max': int(rgb.max()),
                         'ortalama_RGB_kanallari': float(rgb.mean()), 'exif': useful})

    coords, matching = corresponding_points(images)
    pixel_rows, point_overlays = [], []
    for key, rgb in images.items():
        annotated = rgb.copy()
        for index, (x, y) in enumerate(coords[key], start=1):
            assert 0 <= x < rgb.shape[1] and 0 <= y < rgb.shape[0]
            value = rgb[y, x, :]  # NumPy sırası: [y, x, kanal], RGB sırası.
            pixel_rows.append({'nokta': f'P{index}', 'kosul': key, 'x': int(x), 'y': int(y),
                               'R': int(value[0]), 'G': int(value[1]), 'B': int(value[2])})
            cv2.circle(annotated, (int(x), int(y)), 10, (0, 200, 255), 3)
            cv2.putText(annotated, f'P{index}', (int(x) + 12, int(y) - 8), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 70, 200), 2, cv2.LINE_AA)
        if key == 'normal':
            x0, y0, x1, y1 = ROI
            cv2.rectangle(annotated, (x0, y0), (x1 - 1, y1 - 1), (20, 180, 40), 3)
        point_overlays.append(annotated)
        save_rgb(f'noktalar_{key}.png', annotated)

    # Eşik öğrenimi SADECE normal fotoğrafta yapılır. Diğer görüntüler kullanılmaz.
    x0, y0, x1, y1 = ROI
    sample = images['normal'][y0:y1, x0:x1]
    hsv_sample = cv2.cvtColor(sample, cv2.COLOR_RGB2HSV)
    rgb_lo = np.floor(np.percentile(sample, 5, axis=(0, 1)) - 25).clip(0, 255).astype(np.uint8)
    rgb_hi = np.ceil(np.percentile(sample, 95, axis=(0, 1)) + 25).clip(0, 255).astype(np.uint8)
    hsv_lo = np.floor(np.percentile(hsv_sample, 5, axis=(0, 1)) - [7, 35, 100]).clip(0, [179, 255, 255]).astype(np.uint8)
    hsv_hi = np.ceil(np.percentile(hsv_sample, 95, axis=(0, 1)) + [7, 35, 100]).clip(0, [179, 255, 255]).astype(np.uint8)
    thresholds = {'normal_ROI_xyxy': ROI, 'RGB_alt': rgb_lo.tolist(), 'RGB_ust': rgb_hi.tolist(),
                  'HSV_alt': hsv_lo.tolist(), 'HSV_ust': hsv_hi.tolist(),
                  'yontem': 'Normal ROI yüzde 5/95; RGB marj 25; HSV marj H=7, S=35, V=100. Dahil sınırlar.'}
    write_json(OUT / 'esikler.json', thresholds)
    masks, mask_rows = {}, []
    frozen_threshold_hash = hashlib.sha256(json.dumps(thresholds, sort_keys=True).encode()).hexdigest()
    for key, rgb in images.items():
        for space in ('RGB', 'HSV'):
            values = rgb if space == 'RGB' else cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
            low, high = (rgb_lo, rgb_hi) if space == 'RGB' else (hsv_lo, hsv_hi)
            mask = cv2.inRange(values, low, high)
            masks[(key, space)] = mask
            cv2.imencode('.png', mask)[1].tofile(OUT / f'maske_{key}_{space}.png')
            count = int(np.count_nonzero(mask))
            mask_rows.append({'kosul': key, 'uzay': space, 'secilen_piksel': count,
                              'toplam_piksel': int(mask.size), 'alan_orani_yuzde': 100 * count / mask.size,
                              'esik_sha256': frozen_threshold_hash})

    # Sonucu açıklayan ek kontrol: normalde sol alttaki nesne dışı arka plan.
    # Bu ROI eşik belirlemek/ayarlamak için kullanılmaz.
    background_roi = [20, 1025, 230, 1070]
    bx0, by0, bx1, by1 = background_roi
    background = {'ROI_xyxy': background_roi}
    for space in ('RGB', 'HSV'):
        values = masks[('normal', space)][by0:by1, bx0:bx1]
        background[space + '_secilen'] = int(np.count_nonzero(values))
        background[space + '_alan_yuzde'] = float(np.count_nonzero(values) * 100 / values.size)
    background['toplam_piksel'] = (bx1 - bx0) * (by1 - by0)
    yy, xx = np.where(masks[('normal', 'HSV')][by0:by1, bx0:bx1] > 0)
    index = len(xx) // 2
    px, py = int(xx[index] + bx0), int(yy[index] + by0)
    background['ornek_xy'] = [px, py]
    background['ornek_RGB'] = images['normal'][py, px].tolist()
    background['ornek_HSV'] = cv2.cvtColor(images['normal'], cv2.COLOR_RGB2HSV)[py, px].tolist()
    write_json(OUT / 'arka_plan_kontrolu.json', background)

    normal = images['normal']
    base_mean = float(normal.mean())
    transforms = {'parlaklik_40': brightness(normal), 'gama_05': gamma_transform(normal, 0.5),
                  'gama_20': gamma_transform(normal, 2.0)}
    transformation_rows = []
    for key, result in transforms.items():
        stored = display_uint8(result)
        save_rgb(f'{key}.png', stored)
        clipped = (normal.astype(np.float64) + 40 > 255) if key == 'parlaklik_40' else np.zeros_like(normal, bool)
        transformation_rows.append({'donusum': key, 'once_ortalama': base_mean,
                                    'sonra_float_ortalama': float(result.mean()),
                                    'sonra_uint8_ortalama': float(stored.mean()),
                                    'float_ortalama_degisim': float(result.mean()) - base_mean,
                                    'kirpilan_kanal_sayisi': int(clipped.sum()),
                                    'kirpilan_piksel_sayisi': int(np.any(clipped, axis=2).sum()),
                                    'naif_tahmin_ortalama': base_mean + 40 if key == 'parlaklik_40' else '',
                                    'kirpma_nedeniyle_ortalama_kayip': float(np.maximum(normal.astype(float) + 40 - 255, 0).mean()) if key == 'parlaklik_40' else 0})

    x0, y0, x1, y1 = TEXT_CROP
    crop = normal[y0:y1, x0:x1]
    h, w = crop.shape[:2]
    assert h % 4 == 0 and w % 4 == 0
    downs, ups, sampling_rows = {}, {}, []
    for key, interpolation in [('nearest', cv2.INTER_NEAREST), ('area', cv2.INTER_AREA)]:
        down = cv2.resize(crop, (w // 4, h // 4), interpolation=interpolation)
        up = cv2.resize(down, (w, h), interpolation=cv2.INTER_NEAREST)
        downs[key], ups[key] = down, up
        save_rgb(f'kucultme_{key}_kucuk.png', down)
        save_rgb(f'kucultme_{key}_buyutulmus.png', up)
        sampling_rows.append({'yontem': key, 'giris_W': w, 'giris_H': h,
                              'kucuk_W': w // 4, 'kucuk_H': h // 4, 'piksel_sayisi_orani': down.shape[0] * down.shape[1] / (h * w),
                              'yeniden_buyutme_MAE_RGB': float(np.abs(up.astype(float) - crop.astype(float)).mean())})
    save_rgb('yazi_kesiti_orijinal.png', crop)
    write_csv('piksel_degerleri.csv', pixel_rows)
    write_csv('maske_alanlari.csv', mask_rows)
    write_csv('donusum_olcumleri.csv', transformation_rows)
    write_csv('ornekleme_olcumleri.csv', sampling_rows)
    versions = {name: importlib.metadata.version(name) for name in ['numpy', 'opencv-python', 'matplotlib', 'Pillow', 'pypdf']}
    summary = {'kimlik': json.loads((ROOT / 'kimlik.json').read_text(encoding='utf-8')),
               'tahmin_sha256': prediction_hash, 'kaynak_sha256': source_hashes, 'goruntuler': metadata,
               'esikler': thresholds, 'piksel_degerleri': pixel_rows, 'esleme': matching,
               'maske_alanlari': mask_rows, 'arka_plan_kontrolu': background,
               'donusumler': transformation_rows, 'ornekleme': sampling_rows,
               'python': sys.version.split()[0], 'paketler': versions,
               'parametreler': {'b': 40, 'gamma': [0.5, 2.0], 'olcek_kenar': 0.25,
                                'yazi_ROI_xyxy': TEXT_CROP, 'piksel_noktasi_normal_xy': POINTS.tolist()},
               'sinirlar': ['Kamera/kadraj ve perspektif değişti; ışık tek bağımsız değişken değildir.',
                            'Otomatik pozlama ve beyaz dengesi bilinmiyor; mevcut EXIF bunları doğrulamıyor.',
                            'Homografi kâğıt düzlemi için yaklaşık nokta eşlemesidir; şişeye uygulanmaz.',
                            'Maske oranı doğruluk değildir. Etiketli gerçek maske olmadığı için başarı ölçülmedi.',
                            'Tahminler ve açıklamalar Codex yardımıyla hazırlanmıştır.']}
    write_json(OUT / 'ozet.json', summary)
    combined = []
    def add_result(target, experiment, condition, measurement, value, unit, note=''):
        combined.append({'hedef': target, 'deney': experiment, 'kosul': condition,
                         'olcum': measurement, 'deger': value, 'birim': unit, 'aciklama': note})
    for row in metadata:
        for field in ('H', 'W', 'C', 'min', 'max', 'ortalama_RGB_kanallari'):
            add_result('H1', 'sayisal_yapi', row['kosul'], field, row[field], '0-255' if field in ('min','max','ortalama_RGB_kanallari') else 'adet')
    for row in pixel_rows:
        add_result('H1', row['nokta'], row['kosul'], 'RGB', f"{row['R']};{row['G']};{row['B']}", '0-255', f"x={row['x']}; y={row['y']}")
    for row in mask_rows:
        add_result('H2', row['uzay'], row['kosul'], 'alan_orani', row['alan_orani_yuzde'], '%', 'Dogruluk olcutu degildir')
        add_result('H2', row['uzay'], row['kosul'], 'secilen_piksel', row['secilen_piksel'], 'piksel')
    for row in transformation_rows:
        add_result('H3', row['donusum'], 'normal', 'ortalama_float', row['sonra_float_ortalama'], '0-255')
        add_result('H3', row['donusum'], 'normal', 'kirpilan_kanal', row['kirpilan_kanal_sayisi'], 'kanal')
    for row in sampling_rows:
        add_result('H4', row['yontem'], 'normal_yazi_kesiti', 'MAE_RGB', row['yeniden_buyutme_MAE_RGB'], '0-255', 'Okunabilirlik puani degildir')
        add_result('H4', row['yontem'], 'normal_yazi_kesiti', 'piksel_sayisi_orani', row['piksel_sayisi_orani'], 'oran')
    write_csv('sonuc_tablosu.csv', combined)
    write_json(OUT / 'calistirma_kaydi.json', {'utc': datetime.now(timezone.utc).isoformat(),
               'tahmin_kaydi': str(prediction_path.relative_to(ROOT)), 'python': sys.version,
               'paketler': versions, 'deney_py_sha256': sha256(Path(__file__)), 'rapor_py_sha256': sha256(ROOT / 'rapor.py')})
    make_panel(list(images.values()), list(LABELS.values()), 'uc_fotograf.png', 3)
    make_panel(point_overlays, [f'{v}: P1-P3 / normalde yeşil ROI' for v in LABELS.values()], 'nokta_eslemeleri.png', 3)
    order = [(key, space) for space in ('RGB', 'HSV') for key in images]
    make_panel([masks[k] for k in order], [f'{LABELS[k]} / {space}' for k, space in order], 'alti_maske.png', 3)
    make_panel([normal] + [display_uint8(v) for v in transforms.values()],
               ['Özgün', 'Parlaklık +40', 'Gama 0,5', 'Gama 2,0'], 'donusum_karsilastirma.png', 4)
    make_panel([crop, ups['nearest'], ups['area']], ['Özgün kesit', 'NEAREST: 1/4 -> 4x', 'AREA: 1/4 -> NEAREST 4x'],
               'ornekleme_karsilastirma.png', 3)
    from rapor import build_report
    build_report(summary, predictions, images, masks, transforms, crop, ups)
    from notlar import write_notes
    write_notes(summary, predictions)
    print(json.dumps({'ortalama': base_mean, 'esikler': thresholds,
                      'maskeler': [{k: v for k, v in r.items() if k != 'esik_sha256'} for r in mask_rows],
                      'donusumler': transformation_rows, 'esleme': matching,
                      'rapor': 'output/pdf/YZM411_Odev1_230212067_Rapor.pdf'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
