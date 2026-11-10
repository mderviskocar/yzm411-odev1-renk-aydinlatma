"""Ölçümlerden ayrıntılı, izlenebilir deney notu oluşturur."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def write_notes(s, p):
    lines = ['# Ayrıntılı deney notları', '',
             f"Öğrenci: **{s['kimlik']['ad_soyad']} - {s['kimlik']['ogrenci_no']}**", '',
             'Bu metin iki sayfalık PDF raporu destekler; PDF rapor yerine geçmez.', '',
             'Tahminler Codex yardımıyla ilk ölçümden önce kaydedilmiştir. '
             'Rapor ve yorumlar bu ölçümlere dayanır. Önceden bilinmeyen çekim ayarları sonradan varsayılmamıştır.', '',
             '## H1 - Sayısal yapı', '', '**Ön tahmin:** ' + p['H1'], '',
             '| Koşul | H × W × C | Veri türü | Ölçülen min-max | RGB kanal ortalaması |',
             '| --- | --- | --- | --- | --- |']
    for r in s['goruntuler']:
        lines.append(f"| {r['kosul']} | {r['H']} × {r['W']} × {r['C']} | {r['dtype']} | {r['min']}-{r['max']} | {r['ortalama_RGB_kanallari']:.6f} |")
    lines += ['', 'uint8 temsilinin olası aralığı 0-255 olsa da bir görüntünün gerçek en büyük değeri 255 olmak zorunda değildir. '
              'Gölge fotoğrafında en büyük değer 246 ölçülmüştür.', '',
              '| Nokta | Koşul | x | y | R | G | B |', '| --- | --- | --- | --- | --- | --- | --- |']
    for r in s['piksel_degerleri']:
        lines.append(f"| {r['nokta']} | {r['kosul']} | {r['x']} | {r['y']} | {r['R']} | {r['G']} | {r['B']} |")
    lines += ['', '**Ne gördüm?** Üç karşılık gelen kâğıt noktasının RGB değerleri çekimler arasında değişti; gölgede üç kanal da daha düşük çıktı.',
              '**Neden olabilir?** Işık şiddeti/rengi yanında bilinmeyen otomatik kamera ayarları, kâğıt gölgesi ve yaklaşık eşleme hatası etkili olabilir. '
              'Her noktanın lambada normalden daha açık olması gerekmez: P3 daha karanlık çıkmıştır.',
              '**Nasıl kontrol ederim?** Kamera/kâğıt/nesneyi sabitleyip pozlama ve beyaz dengesini kilitleyerek yeniden çekerim. '
              'Sonuçtaki nokta bindirmelerini kontrol eder, tek pikselin yanında küçük komşulukların ortalamasını da incelerim.', '',
              'NumPy erişimi `img[y,x,kanal]` şeklindedir. OpenCV BGR okur; kodda `cv2.COLOR_BGR2RGB` ile RGB elde edilir. '
              'Kâğıt düzleminin homografisi yalnız koordinat eşler; hiçbir fotoğrafı ışık deneyi öncesinde eğip yeniden örneklemez.', '']
    for key, r in s['esleme'].items():
        lines.append(f"- {key}: {r['eslesme']} eşleşme, {r['inlier']} RANSAC iç noktası, medyan yeniden izdüşüm hatası {r['medyan_hata_px']:.3f} piksel. Bu, fiziksel doğruluğun garantisi değildir.")
    lines += ['', '## H2 - Sabit RGB ve HSV eşikleri', '', '**Ön tahmin:** ' + p['H2'], '',
              'ROI yalnız normal ışıklı fotoğrafta sarı şişenin etiket dışındaki bölümünden seçildi. Yüzde 5/95 ve önceden tanımlı marjlarla aralık çıkarıldı. '
              'Aynı alt/üst dizileri diğer iki fotoğrafta değiştirilmeden kullanıldı; maske sonrası morfoloji yapılmadı.', '',
              f"- RGB alt/üst: {s['esikler']['RGB_alt']} / {s['esikler']['RGB_ust']}",
              f"- HSV alt/üst: {s['esikler']['HSV_alt']} / {s['esikler']['HSV_ust']}",
              '- H=0-179; S=0-255; V=0-255. Sınırlar dahildir.', '',
              '| Koşul | Uzay | Seçilen piksel | Toplam piksel | Alan oranı (%) |', '| --- | --- | --- | --- | --- |']
    for r in s['maske_alanlari']:
        lines.append(f"| {r['kosul']} | {r['uzay']} | {r['secilen_piksel']} | {r['toplam_piksel']} | {r['alan_orani_yuzde']:.6f} |")
    bg = s['arka_plan_kontrolu']
    lines += ['', '**Ne gördüm?** Gölgedeki RGB maskesi çok az piksel seçti; HSV maskesi şişeyi daha geniş ölçüde seçmeye devam etti. '
              'Ancak HSV arka planı da seçtiği için daha yüksek maske alanı daha iyi doğruluk anlamına gelmez.',
              '**Neden olabilir?** RGB eşiği kanal parlaklıklarına doğrudan bağlıdır. HSV parlaklığı ayrı kanalda tutar; '
              'seçilen geniş V aralığı gölgeyi kabul edebilir, fakat benzer ton ve doygunluktaki arka plan da aralığa girer.',
              '**Nasıl kontrol ederim?** Üç fotoğrafta aynı eşik dizilerini ve SHA-256 kayıtlarını kontrol ederim. '
              'Gerçek nesne sınırlarını elle işaretleyerek yanlış pozitif ve kaçırılan hedefleri ayrıca ölçerim; bu projede böyle bir doğruluk ölçümü yapılmamıştır.', '',
              '**Sarı bir arka plan neden hedef gibi seçildi?** Kendi örneğimde normal fotoğrafın sol altındaki sarımsı/kahverengi arka plan parçası şişe olmadığı halde HSV eşiğine giriyor. '
              f"Arka plan ROI'si {bg['ROI_xyxy']}; {bg['toplam_piksel']} pikselin {bg['HSV_secilen']}'i (%{bg['HSV_alan_yuzde']:.6f}) HSV ile seçildi, RGB ile %{bg['RGB_alan_yuzde']:.6f} seçildi. "
              f"({bg['ornek_xy'][0]},{bg['ornek_xy'][1]}) noktasında RGB={bg['ornek_RGB']}, HSV={bg['ornek_HSV']}; HSV değeri sabit alt/üst sınırların içindedir. "
              'Renk eşikleri nesne kimliğini veya konumunu bilmediği için bu arka planı hedef gibi seçer. Bu kontrol ROI’si sonuç görüldükten sonra açıklama amacıyla seçilmiş, eşik ayarlamak için kullanılmamıştır.', '',
              '## H3 - Parlaklık ve gama', '']
    for key in ['H3_parlaklik','H3_gama_05','H3_gama_20']:
        lines += ['**Ön tahmin:** ' + p[key], '']
    lines += ['Dönüşümler bağımsızdır: her biri doğrudan özgün normal görüntüye uygulanır. '
              '`J=clip(I+40,0,255)` ve `J=255*(I/255)**gamma`; gamma doğrudan üstür. '
              'NumPy float64 hesabı taşmayı önler; görsel dosyası için yuvarlanmış uint8 saklanır.', '',
              '| Dönüşüm | Önce ortalama | Float sonuç | uint8 kayıt | Float değişim | Kırpılan kanal |',
              '| --- | --- | --- | --- | --- | --- |']
    for r in s['donusumler']:
        lines.append(f"| {r['donusum']} | {r['once_ortalama']:.6f} | {r['sonra_float_ortalama']:.6f} | {r['sonra_uint8_ortalama']:.6f} | {r['float_ortalama_degisim']:.6f} | {r['kirpilan_kanal_sayisi']} |")
    r = s['donusumler'][0]
    lines += ['', '**Tutmayan tahmin:** +40 sonrası ortalama için ilk yaklaşım '
              f"{r['naif_tahmin_ortalama']:.6f} idi; gerçek sonuç {r['sonra_float_ortalama']:.6f}. "
              f"Fark {r['kirpma_nedeniyle_ortalama_kayip']:.6f}; {r['kirpilan_kanal_sayisi']} kanal değeri ve {r['kirpilan_piksel_sayisi']} piksel kırpıldı.",
              '**Ne gördüm?** +40 ve gama 0,5 ortalamayı artırdı, gama 2,0 azalttı. +40 artışı tam 40 olmadı.',
              '**Neden olabilir?** I>215 kanal değerleri +40 sonrası 255 sınırını aşar ve kırpılır. Gama normalize değerleri doğrusal olmayan biçimde değiştirir.',
              '**Nasıl kontrol ederim?** +40 için `mean(J)=mean(I)+40-mean(max(I-215,0))` özdeşliğini ve I>215 kanal sayısını kontrol ederim. '
              'Gama için 64 değerli kontrol pikseli gama 0,5 ile 127,7498 ve gama 2,0 ile 16,0627 olur. '
              'Float ve dosyaya yazılan uint8 ortalamalarının farkı yuvarlamadan gelir.', '',
              '## H4 - Örnekleme', '', '**Ön tahmin:** ' + p['H4'], '',
              'Normal görüntünün (415,380)-(975,620) yazı kesiti 560×240 pikseldir. '
              'İki yöntemle de 140×60 piksele, yani her kenarda 1/4 ve toplam piksel sayısında 1/16’ya inilir. '
              'Gösterim amacıyla iki küçük sonuç da yalnız NEAREST ile 560×240’a büyütülür.', '',
              '| Yöntem | Özgüne göre büyütülmüş sonuç MAE (RGB) |', '| --- | --- |']
    for r in s['ornekleme']:
        lines.append(f"| {r['yontem']} | {r['yeniden_buyutme_MAE_RGB']:.6f} |")
    lines += ['', '**Ne gördüm?** NEAREST sonucunda ince el yazısı çizgileri ve kavisler kesikli/bloklu hale geldi. '
              'AREA sonucu daha silik ve düzgün göründü; küçük yazılar yine özgün ayrıntılarını kaybetti. '
              'Görsel gözlem ön tahminle uyumludur; yapay desen bulunmaması gibi evrensel bir sonuç çıkarılmaz.',
              '**Neden olabilir?** NEAREST az sayıda örnek tutar ve atlanan çizgileri kaybeder; AREA komşu pikselleri ortalar, yüksek frekansları bastırır. '
              'Ön filtreleme sahte desen riskini azaltabilir fakat tüm örneklerde sıfırlama garantisi değildir.',
              '**Nasıl kontrol ederim?** Aynı kesitteki harf, kavis ve ince çizgileri üç görüntüde yan yana incelerim. '
              'Küçük ve büyütülmüş boyutları, NEAREST piksel tekrarlarını ve AREA 4×4 blok ortalamalarını sayısal olarak kontrol ederim. '
              'MAE okunabilirlik puanı değildir; okunabilirlik için ayrıca harf/OCR ölçümü gerekir.', '',
              '**Büyütme kaybolan yazıyı neden geri getirmedi?** Örnek sayısı 16’da bire indi; '
              'NEAREST atılan örnekleri saklamaz, AREA farklı desenleri aynı ortalamaya indirebilir. '
              'Büyütme kalan değerleri çoğaltır; özgün desen tekil olarak belirlenemediği için kaybolan yazıyı yeniden ölçmüş olmaz.', '',
              '## Doğrulama ve kaynak', '',
              '`python dogrula.py` bağımsız aritmetik kontrollerini çalıştırır. Sonuçlar `sonuclar/dogrulama.json` içindedir. '
              'ZIP içinden ayrıca yeniden çalıştırma yapılarak CSV sonuçlarının aynı olduğu kontrol edilir. '
              'Kaynak ve yapay zekâ katkısı `KAYNAK_VE_YZ_BEYANI.md` içinde ayrıntılı açıklanmıştır.', '']
    (ROOT / 'DENEY_NOTLARI.md').write_text('\n'.join(lines), encoding='utf-8')
