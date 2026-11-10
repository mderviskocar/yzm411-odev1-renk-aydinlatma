"""Üretilen sonuçların bağımsız aritmetik ve dosya bütünlüğü kontrolü."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np
import cv2
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent


def run():
    s = json.loads((ROOT / 'sonuclar/ozet.json').read_text(encoding='utf-8'))
    checked = []
    def check(condition, label):
        if not condition:
            raise AssertionError(label)
        checked.append(label)
    def load(path, flag=cv2.IMREAD_COLOR):
        return cv2.imdecode(np.fromfile(ROOT / path, np.uint8), flag)
    raw = load('veri/orijinaller/01_normal.jpg')
    normal_bgr = load('veri/islenmis/normal_isik_90sol.png')
    check(np.array_equal(normal_bgr, np.rot90(raw, 1)), '90 derece donus: tum pikseller eksiksiz korundu')
    images = {'normal': normal_bgr,
              'golge': load('veri/orijinaller/02_golge.jpg'), 'lamba': load('veri/orijinaller/03_lamba.jpg')}
    check(all(hashlib.sha256((ROOT / 'veri/orijinaller' / name).read_bytes()).hexdigest() == value
              for name, value in s['kaynak_sha256'].items()), 'Kaynak JPG SHA-256 degerleri ayni')
    pred = json.loads((ROOT / 'sonuclar/tahmin_kaydi.json').read_text(encoding='utf-8'))
    check(hashlib.sha256((ROOT / 'tahminler.json').read_bytes()).hexdigest() == pred['sha256'], 'Ilk olcum oncesi tahmin kaydi degismedi')
    check(len(s['maske_alanlari']) == 6, 'Alti maske mevcut')
    check(len({row['esik_sha256'] for row in s['maske_alanlari']}) == 1, 'Alti maskede ayni esik kaydi')
    for row in s['maske_alanlari']:
        key, space = row['kosul'], row['uzay']
        rgb = images[key][:, :, ::-1]
        vals = rgb if space == 'RGB' else cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        low, high = np.array(s['esikler'][space + '_alt']), np.array(s['esikler'][space + '_ust'])
        # inRange kullanmadan dogrudan kanal bazli mantiksal kontrol.
        expected = np.all((vals >= low) & (vals <= high), axis=2)
        actual = load(f'sonuclar/maske_{key}_{space}.png', cv2.IMREAD_GRAYSCALE)
        check(np.array_equal(expected, actual > 0), f'{key}/{space}: kayitli maske esiklerle bire bir ayni')
        count = int(expected.sum())
        check(count == row['secilen_piksel'] and abs(count * 100 / expected.size - row['alan_orani_yuzde']) < 1e-12,
              f'{key}/{space}: sayim ve alan orani dogru')
    for row in s['piksel_degerleri']:
        rgb = images[row['kosul']][row['y'], row['x'], ::-1].tolist()
        check(rgb == [row['R'], row['G'], row['B']], f"{row['kosul']}/{row['nokta']}: RGB erisimi dogru")
    rgb = normal_bgr[:, :, ::-1].astype(float)
    bright = s['donusumler'][0]
    lost = np.maximum(rgb - 215, 0).mean()
    check(abs(bright['sonra_float_ortalama'] - (rgb.mean() + 40 - lost)) < 1e-10,
          '+40 ortalama kaybi tam olarak kirpilmaya esit')
    check(bright['kirpilan_kanal_sayisi'] == int((rgb > 215).sum()), 'Kirpilan kanal sayisi dogru')
    for exponent, row in zip([0.5, 2.0], s['donusumler'][1:]):
        expected = np.power(rgb / 255, exponent) * 255
        check(abs(expected.mean() - row['sonra_float_ortalama']) < 1e-10, f'Gamma {exponent} ortalamasi dogru')
    probe = np.array([64.0])
    check(abs(255 * np.sqrt(probe / 255) - 127.7497553813705) < 1e-8, 'Gamma 0.5: 64 yaklasik 128 olur')
    check(abs(255 * (probe / 255) ** 2 - 16.062745098039215) < 1e-8, 'Gamma 2: 64 yaklasik 16 olur')
    crop = load('sonuclar/yazi_kesiti_orijinal.png')
    h, w = crop.shape[:2]
    for key in ['nearest', 'area']:
        small = load(f'sonuclar/kucultme_{key}_kucuk.png')
        big = load(f'sonuclar/kucultme_{key}_buyutulmus.png')
        check(small.shape[:2] == (h // 4, w // 4), f'{key}: her kenar 1/4')
        check(np.array_equal(big, np.repeat(np.repeat(small, 4, axis=0), 4, axis=1)), f'{key}: buyutme yalniz piksel tekraridir')
    check(np.array_equal(load('sonuclar/kucultme_nearest_kucuk.png'), crop[::4, ::4]), 'NEAREST alt orneklemesi dogru')
    block_mean = crop.reshape(h // 4, 4, w // 4, 4, 3).mean(axis=(1, 3))
    check(np.abs(load('sonuclar/kucultme_area_kucuk.png').astype(float) - block_mean).max() <= .5,
          'AREA 4x4 blok ortalamasina en fazla 0.5 yuvarlama uzakliginda')
    pdf = ROOT / f"output/pdf/YZM411_Odev1_{s['kimlik']['ogrenci_no']}_Rapor.pdf"
    reader = PdfReader(pdf)
    check(len(reader.pages) == 2, 'PDF tam iki sayfa')
    check(all(page.extract_text() for page in reader.pages), 'PDF metin katmani mevcut')
    all_text = ''.join(page.extract_text() for page in reader.pages)
    check('230212067' in all_text and 'tahmin tutmadı' in all_text, 'Kimlik ve tutmayan tahmin raporda')
    with (ROOT / 'sonuclar/sonuc_tablosu.csv').open(encoding='utf-8-sig') as stream:
        rows = list(csv.DictReader(stream))
    check({r['hedef'] for r in rows} == {'H1','H2','H3','H4'}, 'Birlesik sonuc tablosu dort hedefi iceriyor')
    result = {'durum': 'BASARILI', 'kontrol_sayisi': len(checked), 'kontroller': checked}
    (ROOT / 'sonuclar/dogrulama.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Tum {len(checked)} kontrol basarili.')


if __name__ == '__main__':
    run()
