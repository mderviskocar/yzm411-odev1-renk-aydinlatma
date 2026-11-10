# Kaynak ve üretici yapay zekâ kullanım beyanı

Öğrenci: **Muhammed Derviş Koçar, 230212067**

## Fotoğraflar

Öğrenci, 10 Kasım 2026 tarihinde üç fotoğrafı kendisinin kamerayla çektiğini ve
üretici yapay zekâ ile düzenlemediğini açıkça beyan etmiştir. Dosya adındaki
“ChatGPT Görseli” ifadesinden fotoğrafın üretildiği sonucu çıkarılmamıştır.

| Kullanıcının verdiği dosya | Projedeki değişmemiş kopya | Koşul |
| --- | --- | --- |
| ChatGPT Görseli 10 Kas 2026 17_24_23.jpg | veri/orijinaller/01_normal.jpg | Normal ışık |
| ChatGPT Görseli 10 Kas 2026 17_24_36.jpg | veri/orijinaller/02_golge.jpg | Gölge |
| ChatGPT Görseli 10 Kas 2026 17_24_46.jpg | veri/orijinaller/03_lamba.jpg | Lamba |

Kaynak dosyalar değiştirilmemiştir; karmaları `sonuclar/ozet.json` içindedir.
Analizde birinci fotoğraf OpenCV ile yalnız 90° sola çevrilmiş ve kayıpsız PNG
olarak saklanmıştır. Döndürmede yeniden örnekleme veya renk düzeltmesi yoktur.
Parlaklık, gama ve küçültme işlemleri deney çıktılarıdır; özgün çekim diye sunulmaz.

İlk döndürme isteğinde üretici görsel aracı denenmiş, yazı ayrıntılarını değiştirdiği
görülerek çıkan dosya reddedilmiştir. Bu üretilen görsel analiz, rapor veya teslim
paketinde kullanılmamıştır. Nihai kaynaklar öğrencinin sağladığı JPG dosyalarıdır.

Kamera modeli, otomatik pozlama ve beyaz dengesi bu dosyaların mevcut EXIF
bilgisinden doğrulanamamıştır. Bunlar hakkında varsayımsal bilgi eklenmemiştir.

## Kullanılan araç ve katkısı

Araç adı: **OpenAI ChatGPT / Codex**.

| Kullanım amacı | Etkilenen dosya | Doğrulama |
| --- | --- | --- |
| Ödev gereksinimlerini çıkarma, deney planı ve ön tahmin | tahminler.json, README.md, DENEY_NOTLARI.md | Ödev PDF'sinin üç sayfasının okunması; tahminlerin ilk ölçümden önce kaydı |
| OpenCV/NumPy analiz kodu ve dosya hazırlama | deney.py, requirements.txt, calistir.bat | Gerçek görüntüler üzerinde çalıştırma; ham CSV ve kaynak SHA-256 değerleri |
| İki sayfalık PDF düzeni ve açıklamalar | rapor.py, output/pdf/*.pdf | PDF sayfa sayısı, metin katmanı ve sayfa görüntülerinin görsel incelemesi |
| Sonuçların sayısal kontrolü | dogrula.py, sonuclar/dogrulama.json | Maskeleri mantıksal kanal karşılaştırmasıyla kontrol; kırpılma özdeşliği, gama, piksel tekrarları ve kaynak bütünlüğü |
| Kaynaklandırma ve paketleme | KAYNAK_VE_YZ_BEYANI.md, paketle.py | Resmî belge incelemesi; ZIP bütünlüğü ve paket içinden yeniden çalıştırma |

Tahminler ve açıklamalar yapay zekâ yardımıyla hazırlanmıştır; öğrencinin bağımsız
olarak yazdığı ön tahminler olarak sunulmaz. Yapılmamış ölçüm yazılmamış ve yönergedeki
örnek sayılar deney sonucu olarak kullanılmamıştır. Doğrulamalar kod/dosya kontrolleridir;
çekim koşullarını veya fotoğrafın kamera kökenini bağımsız olarak kanıtlamaz.

## Kaynaklar

1. Öğr. Gör. Melisa Gözet, **YZM411 Bilgisayarlı Görü, Ödev #1: Renk, Aydınlatma ve
   Örnekleme**, 2026-2027 Güz, kullanıcı tarafından sağlanan üç sayfalık PDF.
   Problem, deney formülleri, parametreler, değerlendirme ve teslim gereksinimleri.
2. OpenCV, **Changing Colorspaces**:
   https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html
   `cvtColor`, `inRange`, BGR/RGB ve HSV'nin 8 bit H=0-179, S/V=0-255 aralıkları.
3. OpenCV, **Geometric Image Transformations**:
   https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html
   `resize`, `INTER_NEAREST`, `INTER_AREA`.
4. NumPy, **numpy.clip**:
   https://numpy.org/doc/stable/reference/generated/numpy.clip.html
   Sayısal değerleri alt/üst sınıra kırpma.

Resmî web kaynakları 10 Kasım 2026'da incelendi. Belge sitelerinin “4.x/stable”
sürümleri kurulandan farklı olabilir; gerçekten kullanılan sürümler
`requirements.txt` ve `sonuclar/ozet.json` içindedir. Hafta 1-2 ders notları ayrıca
sağlanmadığından okunmuş gibi kaynak gösterilmemiştir.

