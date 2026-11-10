# YZM411 Ödev 1 - Renk, Aydınlatma ve Örnekleme

**Muhammed Derviş Koçar - 230212067**  
2026-2027 Güz; son teslim: 10 Kasım 2026.

Bu proje öğrencinin sağladığı üç kamera fotoğrafıyla H1-H4 deneylerini çalıştırır.
PDF rapor ayrıca hazırlanmıştır; kod dosyası rapor yerine geçmez.

- [İki sayfalık PDF raporu aç](output/pdf/YZM411_Odev1_230212067_Rapor.pdf)
- [Tek dosyalık teslim ZIP'ini indir](teslim/YZM411_Odev1_230212067.zip)
- [Birleşik sonuç tablosu](sonuclar/sonuc_tablosu.csv)
- [Kaynak ve yapay zekâ beyanı](KAYNAK_VE_YZ_BEYANI.md)

GitHub deposu: https://github.com/mderviskocar/yzm411-odev1-renk-aydinlatma

## Çalıştırma

Python 3.10.9 ile çalıştırıldı. Paketlerin kullanılan sürümleri `requirements.txt`
ve `sonuclar/ozet.json` içindedir. İnternete bağlı bir ortamda ilk kurulum:

```powershell
python -m pip install -r requirements.txt
```

Ardından proje kökünde:

```powershell
python deney.py
python dogrula.py
```

Bu bilgisayarda `python` PATH'e ekli olmadığından aşağıdaki komut da kullanılabilir:

```powershell
& "$env:LOCALAPPDATA/Programs/Python/Python310/python.exe" deney.py
& "$env:LOCALAPPDATA/Programs/Python/Python310/python.exe" dogrula.py
```

Windows'ta `calistir.bat` dosyasına çift tıklamak da deney ve doğrulamayı çalıştırır.
Kodun resim penceresi veya internet bağlantısı gereksinimi yoktur. PDF, mevcut
Matplotlib PDF arka ucuyla üretilir; Office veya LaTeX gerekmez.

## Dosyalar ve sıra

1. `tahminler.json`: ilk deneyden önce hazırlanmış tahminler; Codex katkısı açıkça belirtilmiştir.
2. `kimlik.json`: öğrenci bilgileri, fotoğraf kaynağı ve bilinmeyen kamera ayarları.
3. `veri/orijinaller/01_normal.jpg`: normal ışık, kullanıcının birinci dosyasının değişmemiş kopyası.
4. `veri/orijinaller/02_golge.jpg`: gölge, kullanıcının ikinci dosyasının değişmemiş kopyası.
5. `veri/orijinaller/03_lamba.jpg`: farklı lamba, kullanıcının üçüncü dosyasının değişmemiş kopyası.
6. `deney.py`: tahmin kaydı, görüntü okuma, H1, H2, H3, H4 ve rapor üretimi sırasını yürütür.
7. `rapor.py`: en fazla iki sayfalık PDF raporu gerçek sonuçlardan üretir.
8. `dogrula.py`: dosya bütünlüğü, bağımsız sayım, formüller ve rapor kontrolü.
9. `sonuclar/`: altı tam çözünürlüklü maske, görseller, CSV tablolar, eşikler ve çalışma kaydı.
10. `output/pdf/YZM411_Odev1_230212067_Rapor.pdf`: teslim raporu, iki sayfa.
11. `KAYNAK_VE_YZ_BEYANI.md`: fotoğraf, yazılım ve yapay zekâ kaynakları.
12. `DENEY_NOTLARI.md`: raporu destekleyen ayrıntılı açıklama ve sınırlamalar.

`notlar.py` ayrıntılı notları, `paketle.py` doğrulanmış dosyalardan teslim ZIP'ini üretir.

`sonuclar/sonuc_tablosu.csv` tüm hedeflerin birleşik sonuç tablosudur.
`piksel_degerleri.csv`, `maske_alanlari.csv`, `donusum_olcumleri.csv` ve
`ornekleme_olcumleri.csv` daha ayrıntılı ham tablolardır. CSV dosyaları UTF-8 BOM
ile kaydedilir; ondalık ayırıcı noktadır.

## Sabit parametreler

- İlk fotoğraf yalnız 90 derece saat yönünün tersine döndürülür ve PNG kaydedilir.
- H1 için normal görüntüde P1=(600,670), P2=(700,720), P3=(850,850) kâğıt noktaları seçilmiştir.
- Çekimler arası hareket nedeniyle aynı koordinatlar kullanılmaz. SIFT eşleşmeleri ve RANSAC
  homografisiyle kâğıt düzlemindeki karşılıklar yaklaşık bulunur; koordinatlar en yakın tam sayıya yuvarlanır.
  Bu işlem kaynak fotoğrafları yeniden örneklemez; yalnız koordinatları taşır.
- SIFT: en çok 6000 özellik; eşleşme oran testi 0,72; RANSAC hata eşiği 3 piksel; tohum 411.
- Renk ROI'si normal görüntüde `[45:105]` x ve `[300:420]` y aralığıdır. `img[y,x]` sırasına dikkat edilir.
- Eşik seçimi yalnız normal fotoğraftan: yüzde 5/95 aralığı; RGB'de ±25, HSV'de H±7, S±35, V±100 marj.
- Eşikler: RGB alt `[138,108,30]`, üst `[203,178,111]`; HSV alt `[14,94,63]`, üst `[30,206,255]`.
  Alt/üst sınırlar dahildir; diğer fotoğraflar için yeniden ayarlanmaz.
- Parlaklık b=+40; gama üstleri 0,5 ve 2,0. İşlemler birbirinden bağımsız olarak özgün normal fotoğrafa uygulanır.
- Görüntü ortalaması tüm RGB kanal örneklerinin aritmetik ortalamasıdır; fiziksel luminans ölçümü değildir.
- Hesaplar float64 üzerinde yapılır. Görsel kayıtları için en yakın tam sayıya yuvarlanıp uint8'e dönülür;
  float ve kayıt ortalamaları ayrı verilir.
- Yazı kesiti normalde `[415:975]` x, `[380:620]` y, yani 560×240 pikseldir.
  NEAREST ve AREA ile 140×60'a küçültülür; ikisi de NEAREST ile 560×240'a büyütülür.
- Arka plan ROI'si `[20,1025,230,1070]` yalnız sonucun açıklanmasında kullanılan ek kontroldür;
  eşik öğreniminde kullanılmamıştır.

## Yöntem sınırları

Kamera ve nesne konumu çekimler arasında tamamen sabit kalmamıştır. Otomatik pozlama
ve beyaz dengesi ayarları bilinmemektedir; mevcut EXIF bunları doğrulamamaktadır.
Bu nedenle ışık tek değişken değildir ve maske oranı değişimi yalnız aydınlatmaya bağlanamaz.
Homografi bu deneysel kusuru ortadan kaldırmaz. Daha kontrollü tekrar için kamera,
şişe ve kâğıt sabitlenmeli, pozlama ve beyaz dengesi kilitlenmelidir.

Maske alanı oranı başarı/doğruluk puanı değildir. Alan dışında kalan gerçek hedef
ve yanlış seçilen arka plan ancak etiketli gerçek maske ile ayrı değerlendirilir.
Küçültme MAE değeri de okunabilirlik veya OCR doğruluğu olarak yorumlanmaz.

## Tahminlerin izlenmesi

`sonuclar/tahmin_kaydi.json` herhangi bir deney ölçümünden önce oluşturulmuştur ve
`tahminler.json` içeriğini, ilk kayıt zamanını ve SHA-256 değerini saklar. Yeniden
çalıştırma tahminleri değiştirmez; dosya değiştirilirse kod hata verir. Yerel zaman
damgası/karması bağımsız bir zaman damgası otoritesi değildir; çalışma sırasını izlemeye yarar.
Tahminler yapay zekâ yardımıyla yazılmıştır; öğrencinin bağımsız çalışması gibi sunulmaz.

## Teslim

Teslim paketi: `YZM411_Odev1_230212067.zip`. İçinde çalıştırılabilir `.py` kodu,
giriş fotoğrafları, PDF rapor, sonuç tablosu ve kaynak beyanı bulunur. Not defteri
yerine yönergede izin verilen `.py` seçeneği kullanılmıştır.

Yönergenin bir maddesi GitHub bağlantısını isteğe bağlı sayarken başlık ve son not
yükleme istemektedir. Bu nedenle PDF rapor ayrıca GitHub'a yüklenmelidir.
Yerel ZIP hazırlamak GitHub'a yüklemek anlamına gelmez; dış yükleme durumu ayrıca bildirilir.

