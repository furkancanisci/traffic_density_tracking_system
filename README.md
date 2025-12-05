# 🚗 Otoyol Trafik Analizi ve Araç Sayma Sistemi

### (Highway Traffic Analysis & Density Tracking System)

Bu proje, bilgisayar görüsü (Computer Vision) teknikleri kullanılarak sabit bir video akışı üzerinden gerçek zamanlı trafik takibi yapan, hareketli araçları arka plandan ayıran ve sayan bir sistemdir. Kullanıcı dostu bir arayüz (GUI) ile görüntü işleme hattının (pipeline) tüm aşamalarını görselleştirir.

-----

## 🧐 Proje Hakkında

Günümüzde akıllı şehir (Smart City) uygulamalarında trafik yoğunluğunun takibi kritik bir öneme sahiptir. Bu proje, sensör maliyetlerini ortadan kaldırarak mevcut güvenlik kameraları üzerinden yazılımsal analiz yapmayı hedefler.

**Temel Özellikler:**

  * **Arka Plan Çıkarma:** Dinamik olarak arka planı modelleme ve hareketli nesneleri ayırma.
  * **Gölge Algılama:** Hareket eden araçların gölgelerini nesneden ayırt edebilme.
  * **Gürültü Filtreleme:** Rüzgar, ışık yansıması gibi çevresel gürültüleri temizleme.
  * **Gerçek Zamanlı Sayım:** Belirlenen sanal çizgiden geçen araçları çift yönlü sayabilme altyapısı.
  * **Multi-View Dashboard:** İşlemin 4 farklı aşamasını (Ham, Maske, Temiz, Sonuç) tek ekranda sunma.

-----

## ⚙️ Sistem Mimarisi ve Algoritma

Proje, temel olarak 5 aşamalı bir görüntü işleme boru hattından (pipeline) oluşur.

### 1\. Arka Plan Modelleme (Background Subtraction)

Statik kameralarda hareketli nesneleri tespit etmek için **Gaussian Mixture-based Background/Foreground Segmentation (MOG2)** algoritması kullanılmıştır.

  * **Neden MOG2?** Basit "Frame Difference" yöntemlerine göre ışık değişimlerine (güneşin hareketi, bulut geçişi) karşı adaptiftir. Her pikselin geçmişini bir "Gaussian Karışım Modeli" ile tutar.
  * **Kod:** `cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40, detectShadows=True)`

### 2\. İkili Eşikleme (Binary Thresholding)

MOG2 algoritması varsayılan olarak gölgeleri gri ton (değer: 127) olarak işaretler. Araçların net sınırlarını belirlemek için gölgeler maskeden atılır.

  * **İşlem:** Piksel değeri 250'den büyükse (hareketli nesne) Beyaz, değilse Siyah yapılır.

### 3\. Morfolojik İşlemler (Morphological Operations)

Ham maske üzerinde oluşan "Tuz-Biber" gürültülerini gidermek ve araç parçalarını birleştirmek için kullanılır.

  * **Opening (Açma):** `Erosion` ardından `Dilation` uygulanır. Arka plandaki küçük beyaz noktaları (gürültüleri) siler.
  * **Closing (Kapama):** `Dilation` ardından `Erosion` uygulanır. Aracın camı gibi yansıma yapan ve maskede delik oluşturan kısımları doldurur.

### 4\. Kontur Tespiti ve Filtreleme (Contour Detection)

Temizlenen maske üzerindeki beyaz adacıkların sınırları (`cv2.findContours`) çıkarılır.

  * **Alan Filtresi:** Yanlış tespitleri önlemek için alanı `MIN_AREA` (örn: 500 piksel) değerinden küçük olan nesneler işleme alınmaz.

### 5\. Nesne Takibi ve Sayma (Tracking & Counting)

Her tespit edilen aracın geometrik merkezi (Centroid) hesaplanır.
$$C_x = x + \frac{w}{2}, \quad C_y = y + \frac{h}{2}$$
Ekrana sanal bir çizgi çekilir. Aracın merkezi bu çizginin koordinat aralığına (`line_y ± offset`) girdiği anda sayaç artırılır ve görsel geri bildirim verilir.

-----

## 🛠 Kullanılan Teknolojiler

| Teknoloji | Amaç |
| :--- | :--- |
| **Python 3.10+** | Ana programlama dili. |
| **OpenCV (cv2)** | Görüntü işleme, MOG2 algoritması ve çizim işlemleri. |
| **NumPy** | Matris tabanlı görüntü manipülasyonu ve matematiksel hesaplamalar. |
| **Tkinter** | Kullanıcı Arayüzü (GUI) ve pencere yönetimi. |
| **Pillow (PIL)** | OpenCV görüntü formatının (BGR) Tkinter formatına (ImageTk) dönüştürülmesi. |

-----

## 🚀 Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

**1. Gereksinimlerin Yüklenmesi**
Terminal veya komut satırını açarak gerekli kütüphaneleri yükleyin:

```bash
pip install opencv-python numpy pillow
```

**2. Video Kaynağının Eklenmesi**
Proje dizinine `traffic.mp4` adında bir video dosyası ekleyin. (Sabit açılı bir otoyol videosu önerilir).

**3. Projenin Başlatılması**

```bash
python main.py
```

-----

## 🔧 Konfigürasyon

`main.py` dosyasının başındaki sabitleri değiştirerek projeyi kendi videonuza göre optimize edebilirsiniz:

```python
VIDEO_PATH = 'traffic.mp4'  # İşlenecek video dosyası
MIN_AREA = 500              # Araç kabul edilecek minimum piksel boyutu
RESIZE_DIM = (640, 360)     # Panel boyutları
LINE_POS_RATIO = 0.6        # Sayım çizgisinin dikey konumu (0.0 - 1.0 arası)
```

-----

## 📸 Sonuçlar ve Ekran Görüntüleri

Uygulama çalıştığında **4 panelli bir arayüz** sunar:

1.  **Sol Üst:** Orijinal Video (Input).
2.  **Sağ Üst:** MOG2 Maskesi (Arka plan çıkarılmış ham görüntü, gölgeler dahil).
3.  **Sol Alt:** Temizlenmiş Maske (Threshold ve Morfolojik işlemler sonrası).
4.  **Sağ Alt:** Tespit (Bounding Box) ve Sayım sonucu.

## 📝 Lisans

Bu proje eğitim amaçlı hazırlanmıştır. Açık kaynak kodludur.