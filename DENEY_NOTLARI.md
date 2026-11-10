# Ayrıntılı deney notları

Öğrenci: **Muhammed Derviş Koçar - 230212067**

Bu metin iki sayfalık PDF raporu destekler; PDF rapor yerine geçmez.

Tahminler Codex yardımıyla ilk ölçümden önce kaydedilmiştir. Rapor ve yorumlar bu ölçümlere dayanır. Önceden bilinmeyen çekim ayarları sonradan varsayılmamıştır.

## H1 - Sayısal yapı

**Ön tahmin:** Aynı fiziksel kâğıt bölgesindeki üç noktanın RGB değerlerinin ışık koşulları arasında değişmesini bekliyorum. Aydınlatma ve olası otomatik kamera ayarları kanal değerlerini birlikte etkileyebilir.

| Koşul | H × W × C | Veri türü | Ölçülen min-max | RGB kanal ortalaması |
| --- | --- | --- | --- | --- |
| normal | 1080 × 1440 × 3 | uint8 | 0-255 | 149.526658 |
| golge | 1152 × 1536 × 3 | uint8 | 0-246 | 63.571883 |
| lamba | 1152 × 1536 × 3 | uint8 | 0-255 | 125.946523 |

uint8 temsilinin olası aralığı 0-255 olsa da bir görüntünün gerçek en büyük değeri 255 olmak zorunda değildir. Gölge fotoğrafında en büyük değer 246 ölçülmüştür.

| Nokta | Koşul | x | y | R | G | B |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | normal | 600 | 670 | 152 | 143 | 126 |
| P2 | normal | 700 | 720 | 154 | 148 | 134 |
| P3 | normal | 850 | 850 | 155 | 149 | 135 |
| P1 | golge | 791 | 732 | 80 | 76 | 64 |
| P2 | golge | 890 | 783 | 87 | 84 | 79 |
| P3 | golge | 1037 | 912 | 79 | 78 | 73 |
| P1 | lamba | 755 | 719 | 169 | 162 | 144 |
| P2 | lamba | 846 | 778 | 166 | 164 | 149 |
| P3 | lamba | 976 | 920 | 134 | 130 | 119 |

**Ne gördüm?** Üç karşılık gelen kâğıt noktasının RGB değerleri çekimler arasında değişti; gölgede üç kanal da daha düşük çıktı.
**Neden olabilir?** Işık şiddeti/rengi yanında bilinmeyen otomatik kamera ayarları, kâğıt gölgesi ve yaklaşık eşleme hatası etkili olabilir. Her noktanın lambada normalden daha açık olması gerekmez: P3 daha karanlık çıkmıştır.
**Nasıl kontrol ederim?** Kamera/kâğıt/nesneyi sabitleyip pozlama ve beyaz dengesini kilitleyerek yeniden çekerim. Sonuçtaki nokta bindirmelerini kontrol eder, tek pikselin yanında küçük komşulukların ortalamasını da incelerim.

NumPy erişimi `img[y,x,kanal]` şeklindedir. OpenCV BGR okur; kodda `cv2.COLOR_BGR2RGB` ile RGB elde edilir. Kâğıt düzleminin homografisi yalnız koordinat eşler; hiçbir fotoğrafı ışık deneyi öncesinde eğip yeniden örneklemez.

- golge: 397 eşleşme, 313 RANSAC iç noktası, medyan yeniden izdüşüm hatası 0.978 piksel. Bu, fiziksel doğruluğun garantisi değildir.
- lamba: 516 eşleşme, 420 RANSAC iç noktası, medyan yeniden izdüşüm hatası 1.041 piksel. Bu, fiziksel doğruluğun garantisi değildir.

## H2 - Sabit RGB ve HSV eşikleri

**Ön tahmin:** Gölgede sabit RGB maskesinin alan oranının normal ışığa göre azalmasını, HSV oranının ise daha az değişmesini bekliyorum. HSV tonu parlaklıktan kısmen ayırır; ancak doygunluk, parlama ve lambanın rengi nedeniyle tam dayanıklılık beklemiyorum.

ROI yalnız normal ışıklı fotoğrafta sarı şişenin etiket dışındaki bölümünden seçildi. Yüzde 5/95 ve önceden tanımlı marjlarla aralık çıkarıldı. Aynı alt/üst dizileri diğer iki fotoğrafta değiştirilmeden kullanıldı; maske sonrası morfoloji yapılmadı.

- RGB alt/üst: [138, 108, 30] / [203, 178, 111]
- HSV alt/üst: [14, 94, 63] / [30, 206, 255]
- H=0-179; S=0-255; V=0-255. Sınırlar dahildir.

| Koşul | Uzay | Seçilen piksel | Toplam piksel | Alan oranı (%) |
| --- | --- | --- | --- | --- |
| normal | RGB | 117437 | 1555200 | 7.551247 |
| normal | HSV | 152615 | 1555200 | 9.813207 |
| golge | RGB | 623 | 1769472 | 0.035208 |
| golge | HSV | 135758 | 1769472 | 7.672232 |
| lamba | RGB | 101380 | 1769472 | 5.729393 |
| lamba | HSV | 145672 | 1769472 | 8.232512 |

**Ne gördüm?** Gölgedeki RGB maskesi çok az piksel seçti; HSV maskesi şişeyi daha geniş ölçüde seçmeye devam etti. Ancak HSV arka planı da seçtiği için daha yüksek maske alanı daha iyi doğruluk anlamına gelmez.
**Neden olabilir?** RGB eşiği kanal parlaklıklarına doğrudan bağlıdır. HSV parlaklığı ayrı kanalda tutar; seçilen geniş V aralığı gölgeyi kabul edebilir, fakat benzer ton ve doygunluktaki arka plan da aralığa girer.
**Nasıl kontrol ederim?** Üç fotoğrafta aynı eşik dizilerini ve SHA-256 kayıtlarını kontrol ederim. Gerçek nesne sınırlarını elle işaretleyerek yanlış pozitif ve kaçırılan hedefleri ayrıca ölçerim; bu projede böyle bir doğruluk ölçümü yapılmamıştır.

**Sarı bir arka plan neden hedef gibi seçildi?** Kendi örneğimde normal fotoğrafın sol altındaki sarımsı/kahverengi arka plan parçası şişe olmadığı halde HSV eşiğine giriyor. Arka plan ROI'si [20, 1025, 230, 1070]; 9450 pikselin 9247'i (%97.851852) HSV ile seçildi, RGB ile %0.000000 seçildi. (69,1047) noktasında RGB=[72, 55, 37], HSV=[15, 124, 72]; HSV değeri sabit alt/üst sınırların içindedir. Renk eşikleri nesne kimliğini veya konumunu bilmediği için bu arka planı hedef gibi seçer. Bu kontrol ROI’si sonuç görüldükten sonra açıklama amacıyla seçilmiş, eşik ayarlamak için kullanılmamıştır.

## H3 - Parlaklık ve gama

**Ön tahmin:** Parlaklık +40 işleminde görüntü ortalamasının tam 40 artacağını ilk yaklaşım olarak tahmin ediyorum. Bu tahmin hiçbir kanal değerinin 255 sınırında kırpılmadığını varsayar; ölçüm bu varsayımı sınayacaktır.

**Ön tahmin:** Gama 0,5 dönüşümünde görüntü ortalamasının artmasını bekliyorum. 0 ile 1 arasındaki normalize değerlerin karekökü daha büyük olduğundan özellikle koyu ve orta tonlar aydınlanacaktır.

**Ön tahmin:** Gama 2,0 dönüşümünde görüntü ortalamasının azalmasını bekliyorum. Normalize değerlerin karesi daha küçük olduğundan orta tonlar kararacaktır.

Dönüşümler bağımsızdır: her biri doğrudan özgün normal görüntüye uygulanır. `J=clip(I+40,0,255)` ve `J=255*(I/255)**gamma`; gamma doğrudan üstür. NumPy float64 hesabı taşmayı önler; görsel dosyası için yuvarlanmış uint8 saklanır.

| Dönüşüm | Önce ortalama | Float sonuç | uint8 kayıt | Float değişim | Kırpılan kanal |
| --- | --- | --- | --- | --- | --- |
| parlaklik_40 | 149.526658 | 188.301673 | 188.301673 | 38.775015 | 536360 |
| gama_05 | 149.526658 | 188.154450 | 188.163809 | 38.627792 | 0 |
| gama_20 | 149.526658 | 102.665625 | 102.648435 | -46.861033 | 0 |

**Tutmayan tahmin:** +40 sonrası ortalama için ilk yaklaşım 189.526658 idi; gerçek sonuç 188.301673. Fark 1.224985; 536360 kanal değeri ve 254666 piksel kırpıldı.
**Ne gördüm?** +40 ve gama 0,5 ortalamayı artırdı, gama 2,0 azalttı. +40 artışı tam 40 olmadı.
**Neden olabilir?** I>215 kanal değerleri +40 sonrası 255 sınırını aşar ve kırpılır. Gama normalize değerleri doğrusal olmayan biçimde değiştirir.
**Nasıl kontrol ederim?** +40 için `mean(J)=mean(I)+40-mean(max(I-215,0))` özdeşliğini ve I>215 kanal sayısını kontrol ederim. Gama için 64 değerli kontrol pikseli gama 0,5 ile 127,7498 ve gama 2,0 ile 16,0627 olur. Float ve dosyaya yazılan uint8 ortalamalarının farkı yuvarlamadan gelir.

## H4 - Örnekleme

**Ön tahmin:** Her iki yöntemde de dörtte bire küçülünce ince yazı ayrıntılarının kaybolmasını bekliyorum. En yakın komşuda kesintili çizgi ve yapay desen, alan ortalamasında daha düzgün fakat gri ve silik harfler bekliyorum.

Normal görüntünün (415,380)-(975,620) yazı kesiti 560×240 pikseldir. İki yöntemle de 140×60 piksele, yani her kenarda 1/4 ve toplam piksel sayısında 1/16’ya inilir. Gösterim amacıyla iki küçük sonuç da yalnız NEAREST ile 560×240’a büyütülür.

| Yöntem | Özgüne göre büyütülmüş sonuç MAE (RGB) |
| --- | --- |
| nearest | 5.912215 |
| area | 4.221203 |

**Ne gördüm?** NEAREST sonucunda ince el yazısı çizgileri ve kavisler kesikli/bloklu hale geldi. AREA sonucu daha silik ve düzgün göründü; küçük yazılar yine özgün ayrıntılarını kaybetti. Görsel gözlem ön tahminle uyumludur; yapay desen bulunmaması gibi evrensel bir sonuç çıkarılmaz.
**Neden olabilir?** NEAREST az sayıda örnek tutar ve atlanan çizgileri kaybeder; AREA komşu pikselleri ortalar, yüksek frekansları bastırır. Ön filtreleme sahte desen riskini azaltabilir fakat tüm örneklerde sıfırlama garantisi değildir.
**Nasıl kontrol ederim?** Aynı kesitteki harf, kavis ve ince çizgileri üç görüntüde yan yana incelerim. Küçük ve büyütülmüş boyutları, NEAREST piksel tekrarlarını ve AREA 4×4 blok ortalamalarını sayısal olarak kontrol ederim. MAE okunabilirlik puanı değildir; okunabilirlik için ayrıca harf/OCR ölçümü gerekir.

**Büyütme kaybolan yazıyı neden geri getirmedi?** Örnek sayısı 16’da bire indi; NEAREST atılan örnekleri saklamaz, AREA farklı desenleri aynı ortalamaya indirebilir. Büyütme kalan değerleri çoğaltır; özgün desen tekil olarak belirlenemediği için kaybolan yazıyı yeniden ölçmüş olmaz.

## Doğrulama ve kaynak

`python dogrula.py` bağımsız aritmetik kontrollerini çalıştırır. Sonuçlar `sonuclar/dogrulama.json` içindedir. ZIP içinden ayrıca yeniden çalıştırma yapılarak CSV sonuçlarının aynı olduğu kontrol edilir. Kaynak ve yapay zekâ katkısı `KAYNAK_VE_YZ_BEYANI.md` içinde ayrıntılı açıklanmıştır.
