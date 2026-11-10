"""İki sayfalık Türkçe PDF; gerçek deney sonuçlarından yeniden üretilir."""
from pathlib import Path
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Unicode eşlemesi ve Türkçe metnin PDF'den doğru kopyalanması için TrueType.
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

ROOT = Path(__file__).resolve().parent
INK, MUTED, BLUE = '#162636', '#45576a', '#145e79'


def text(fig, x, y, content, size=8, width=125, color=INK, weight='normal', line_height=0.0135):
    lines = []
    for paragraph in content.split('\n'):
        lines.extend(textwrap.wrap(paragraph, width=width, break_long_words=False, break_on_hyphens=False) or [''])
    fig.text(x, y, '\n'.join(lines), fontsize=size, color=color, weight=weight, ha='left', va='top',
             linespacing=1.28, fontfamily='DejaVu Sans')
    return y - line_height * len(lines)


def image(fig, box, pixels, title, size=7.4):
    ax = fig.add_axes(box)
    ax.imshow(pixels, cmap='gray' if pixels.ndim == 2 else None, vmin=0, vmax=255, interpolation='nearest')
    ax.axis('off')
    ax.set_title(title, fontsize=size, color=INK, pad=4)


def table(fig, box, rows, columns, widths=None, fontsize=7.0):
    ax = fig.add_axes(box)
    ax.axis('off')
    t = ax.table(cellText=rows, colLabels=columns, cellLoc='left', colLoc='left',
                 colWidths=widths, loc='center', bbox=[0, 0, 1, 1])
    t.auto_set_font_size(False)
    t.set_fontsize(fontsize)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor('#d5dfe5')
        cell.set_linewidth(0.4)
        cell.PAD = 0.08
        cell.set_text_props(color=INK)
        if r == 0:
            cell.set_facecolor('#e4f0f4')
            cell.set_text_props(weight='bold')
        elif r % 2 == 0:
            cell.set_facecolor('#f3f6f8')
    return t


def page(title, number, identity):
    fig = plt.figure(figsize=(8.2677, 11.6929), facecolor='white')
    fig.text(.055, .967, 'YZM411  /  RENK, AYDINLATMA VE ÖRNEKLEME', fontsize=12,
             weight='bold', color=BLUE, va='top')
    fig.text(.055, .942, f"{identity['ad_soyad']}  |  {identity['ogrenci_no']}  |  10 Kasım 2026", fontsize=8.5, color=MUTED, va='top')
    fig.text(.055, .922, title, fontsize=10, color=INK, weight='bold', va='top')
    fig.text(.055, .024, 'Gerçek dosyalardan ölçüm • Kod, ham tablolar ve kaynak beyanı ZIP içindedir.', fontsize=6.8, color=MUTED)
    fig.text(.945, .024, str(number) + ' / 2', ha='right', fontsize=7.5, color=MUTED)
    return fig


def build_report(s, p, images, masks, transforms, crop, ups):
    folder = ROOT / 'output/pdf'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"YZM411_Odev1_{s['kimlik']['ogrenci_no']}_Rapor.pdf"
    keys = ['normal', 'golge', 'lamba']
    labels = ['Normal ışık', 'Gölge', 'Lamba']
    m = {(r['kosul'], r['uzay']): r['alan_orani_yuzde'] for r in s['maske_alanlari']}
    with PdfPages(path, metadata={'Title': 'YZM411 Ödev 1 - Renk, Aydınlatma ve Örnekleme',
                                 'Author': s['kimlik']['ad_soyad'], 'Subject': 'Ölçüm ve tahmin karşılaştırması'}) as pdf:
        fig = page('1. Sayısal temsil ve sabit renk eşikleri', 1, s['kimlik'])
        text(fig, .055, .900, 'Düzenek: Sarı şişe, beyaz kâğıt ve el yazısı. Üç çekim öğrenciye aittir (öğrenci beyanı). '
             'Kadraj/perspektif değişmiştir; otomatik pozlama ve beyaz dengesi bilinmiyor. Bu yüzden yalnız ışığın değiştiği iddia edilmez.', size=7.9, width=128)
        text(fig, .055, .858, 'H1 - Tahmin: ' + p['H1'], size=7.7, width=130)
        for i, (key, label) in enumerate(zip(keys, labels)):
            dims = images[key].shape
            image(fig, [.055 + i * .302, .648, .287, .167], images[key], f'{label} - {dims[1]}×{dims[0]}×3')
        rows = []
        for point in ('P1', 'P2', 'P3'):
            vals = []
            for key in keys:
                r = next(r for r in s['piksel_degerleri'] if r['nokta'] == point and r['kosul'] == key)
                vals.append(f"({r['x']},{r['y']}) : ({r['R']},{r['G']},{r['B']})")
            rows.append([point] + vals)
        table(fig, [.055, .575, .89, .068], rows, ['Nokta', 'Normal: (x,y) : RGB', 'Gölge: (x,y) : RGB', 'Lamba: (x,y) : RGB'],
              widths=[.07, .31, .31, .31], fontsize=6.8)
        text(fig, .055, .562, 'H1 - Ölçüm / yorum / kontrol: Tüm görüntüler uint8; ölçülen aralık ' +
             ', '.join(f"{label} {v['min']}-{v['max']}" for label, v in zip(labels, s['goruntuler'])) +
             '. BGR, cv2.COLOR_BGR2RGB ile çevrildi; erişim img[y,x,kanal]. Aynı kâğıt düzlemindeki noktalar SIFT + homografiyle yaklaşık eşlendi; RGB değişti. '
             'Işık ve kamera etkileri ayrışmıyor; kontrol için sabit kamera, kilitli pozlama/beyaz dengesiyle yeniden çekim gerekir.', size=7.6, width=133)
        text(fig, .055, .494, 'H2 - Tahmin: ' + p['H2'], size=7.7, width=130)
        th = s['esikler']
        text(fig, .055, .453, f"Sabit eşikler: RGB {th['RGB_alt']} - {th['RGB_ust']}; HSV {th['HSV_alt']} - {th['HSV_ust']}. "
             'H: 0-179, S/V: 0-255. ROI: (45,300)-(105,420); yalnız normal çekim.', size=7.0, width=143)
        for row, space in enumerate(('RGB', 'HSV')):
            for col, (key, label) in enumerate(zip(keys, labels)):
                image(fig, [.055 + col * .302, .310 - row * .126, .287, .104], masks[(key, space)],
                      f'{label} / {space}: %{m[(key, space)]:.2f}', size=7.1)
        rows = []
        for key, label in zip(keys, labels):
            rgb = next(r for r in s['maske_alanlari'] if r['kosul'] == key and r['uzay'] == 'RGB')
            hsv = next(r for r in s['maske_alanlari'] if r['kosul'] == key and r['uzay'] == 'HSV')
            rows.append([label, str(rgb['toplam_piksel']), f"{rgb['secilen_piksel']} / %{rgb['alan_orani_yuzde']:.3f}",
                         f"{hsv['secilen_piksel']} / %{hsv['alan_orani_yuzde']:.3f}"])
        table(fig, [.055, .101, .89, .067], rows, ['Koşul', 'Görüntü pikseli', 'RGB: sayı / alan oranı', 'HSV: sayı / alan oranı'], fontsize=7)
        rgb_change = abs(m[('golge', 'RGB')] - m[('normal', 'RGB')])
        hsv_change = abs(m[('golge', 'HSV')] - m[('normal', 'HSV')])
        status = 'tuttu' if hsv_change < rgb_change and m[('golge','RGB')] < m[('normal','RGB')] else 'tam tutmadı'
        bg = s['arka_plan_kontrolu']
        text(fig, .055, .090, f'H2 - Sonuç: Gölgede alan değişimi RGB {rgb_change:.2f}, HSV {hsv_change:.2f} yüzde puan; tahmin {status}. '
             f"Sarı arka plan neden hedef gibi seçildi? Normal çekimin sol alt arka plan ROI'sinin %{bg['HSV_alan_yuzde']:.2f}'i HSV eşiğine girdi; "
             f"örnek ({bg['ornek_xy'][0]},{bg['ornek_xy'][1]}) HSV={bg['ornek_HSV']}. Benzer renk nesne kimliği değildir. "
             'Kontrol: arka plan ROI sayımı (20,1025)-(230,1070) ve elle nesne maskesi. Alan oranı doğruluk değildir; kadraj da oranı etkiler.',
             size=7.3, width=136)
        pdf.savefig(fig)
        plt.close(fig)

        fig = page('2. Parlaklık, gama, örnekleme ve değerlendirme', 2, s['kimlik'])
        text(fig, .055, .900, 'H3 - Tahmin (+40): ' + p['H3_parlaklik'], size=7.6, width=133)
        text(fig, .055, .860, 'Tahmin (γ=0,5): ' + p['H3_gama_05'], size=7.6, width=133)
        text(fig, .055, .820, 'Tahmin (γ=2,0): ' + p['H3_gama_20'], size=7.6, width=133)
        normal_mean = s['goruntuler'][0]['ortalama_RGB_kanallari']
        all_images = [images['normal']] + [np.rint(v).astype(np.uint8) for v in transforms.values()]
        all_labels = [f'Özgün: μ={normal_mean:.2f}', '+40 parlaklık', 'Gama 0,5', 'Gama 2,0']
        for i, (pixels, label) in enumerate(zip(all_images, all_labels)):
            image(fig, [.055 + i * .225, .626, .213, .149], pixels, label, size=7.2)
        rows = []
        for label, r in zip(['+40', 'γ=0,5', 'γ=2,0'], s['donusumler']):
            rows.append([label, f"{r['once_ortalama']:.3f}", f"{r['sonra_float_ortalama']:.3f}",
                         f"{r['sonra_uint8_ortalama']:.3f}", f"{r['float_ortalama_degisim']:+.3f}"])
        table(fig, [.055, .548, .89, .063], rows, ['Dönüşüm', 'Önce μ', 'Sonra μ (float)', 'Kayıt μ (uint8)', 'Δμ (float)'], fontsize=7.2)
        br = s['donusumler'][0]
        text(fig, .055, .536, 'H3 - Ölçüm / yorum: J=clip(I+40,0,255); gama için J=255·(I/255)^γ. Önce float64 kullanıldı. '
             f"+40 tahmini {br['naif_tahmin_ortalama']:.3f}, ölçüm {br['sonra_float_ortalama']:.3f}: tahmin tutmadı. "
             f"{br['kirpilan_kanal_sayisi']} kanal değeri ({br['kirpilan_piksel_sayisi']} piksel) kırpıldı; ortalamadaki kayıp {br['kirpma_nedeniyle_ortalama_kayip']:.3f}. "
             'Kontrol: I>215 değerlerini sayıp taşan miktarın ortalamasını hesaplamak. Gama tahminleri tuttu; kontrol pikseli 64, γ=0,5 ile 127,75; γ=2 ile 16,06 olur. Kayıt yuvarlaması tabloda ayrıdır.',
             size=7.7, width=130)
        text(fig, .055, .462, 'H4 - Tahmin: ' + p['H4'], size=7.7, width=130)
        for i, (pixels, label) in enumerate(zip([crop, ups['nearest'], ups['area']],
                                              ['Özgün yazı kesiti: 560×240', 'NEAREST: 140×60 -> 560×240', 'AREA: 140×60 -> NEAREST 4x'])):
            image(fig, [.055 + i * .302, .299, .287, .105], pixels, label, size=6.7)
        sampling = s['ornekleme']
        text(fig, .055, .284, 'H4 - Ölçüm / yorum / kontrol: Her kenar 1/4; piksel sayısı 1/16 (%6,25). '
             f"Özgüne göre RGB mutlak hata ortalaması: NEAREST {sampling[0]['yeniden_buyutme_MAE_RGB']:.2f}, AREA {sampling[1]['yeniden_buyutme_MAE_RGB']:.2f}; "
             'bu hata okunabilirlik puanı değildir. NEAREST ince çizgileri kesikli, AREA daha silik gösterir. '
             'Büyütme kaybolan yazıyı neden geri getirmedi? Atlanan/ortalaması alınan örnekler artık yoktur; büyütme yalnız kalan pikselleri çoğaltır. '
             'Kontrol: aynı kesitteki harflerin ince çizgilerini özgün ve iki büyütülmüş görüntüde bire bir karşılaştırmak.', size=7.7, width=130)
        text(fig, .055, .191, 'Sınırlar ve yeniden üretim: Üç piksel kâğıt düzleminde yaklaşık eşlenmiştir; alt piksel ve yuvarlama hatası vardır. '
             'Şişe eğridir, bu eşleme şişeye genellenmez. Fotoğraflar yeniden boyutlandırılmadan maskelendi; ilk fotoğraf yalnız 90° sola çevrildi. '
             'Kod: deney.py; tüm parametreler, paket sürümleri, SHA-256 ve ham sonuçlar sonuclar/ içinde. Çalıştırma: python deney.py.',
             size=7.6, width=132)
        text(fig, .055, .122, 'Yapay zekâ beyanı: OpenAI ChatGPT / Codex; tahminler.json, deney.py, rapor.py, açıklamalar ve raporun hazırlanmasında kullanıldı. '
             'Tahminler öğrencinin bağımsız tahminleri olarak sunulmaz. Doğrulama: kaynak karmaları, sabit eşikler, sayım ve dönüşüm kontrolleri, yeniden çalıştırma ve PDF görsel incelemesi. '
             'Önceki üretici döndürme denemesi reddedildi; üretilen görüntü kullanılmadı. Kaynaklar: ödev yönergesi, OpenCV/NumPy belgeleri; ayrıntı KAYNAK_VE_YZ_BEYANI.md içinde.',
             size=7.4, width=136)
        pdf.savefig(fig)
        plt.close(fig)
    return path
