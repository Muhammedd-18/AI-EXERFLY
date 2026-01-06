# ✈️ AI Motion Controlled Flight Game (Exergame)

**Ders:** Görsel Programlama  
**Proje Türü:** Görüntü İşleme Tabanlı Egzersiz Oyunu

Bu proje, Python ve Yapay Zeka (AI) teknolojileri kullanılarak geliştirilmiş, kullanıcının **vücut hareketleriyle** yönettiği interaktif bir uçuş simülasyonudur.

Klasik oyunların aksine, bu proje kullanıcıyı bilgisayar başında oturmaya değil, **hareket etmeye** teşvik eder. MediaPipe teknolojisi ile oyuncunun iskelet sistemi algılanır ve kollar bir uçağın kanatları gibi kullanılır.

## ❤️ Sağlık ve Egzersiz Odaklı Yaklaşım
Günümüzde bilgisayar başında uzun süre hareketsiz kalmak (sedanter yaşam), duruş bozukluklarına ve kas ağrılarına yol açmaktadır. Bu proje, **"Exergame" (Egzersiz-Oyun)** mantığıyla şu faydaları sağlar:

* **Omuz ve Sırt Egzersizi:** Oyuncunun kollarını 90 derece ve üzerinde tutması (T-Pose), Deltoid (omuz) ve Trapezius (sırt) kaslarının aktif çalışmasını sağlar.
* **Postür (Duruş) Düzeltme:** Uçağı kontrol etmek için dik durmak gerektiğinden, oyuncunun omurga duruşunu düzeltmesine yardımcı olur.
* **Aktif Mola:** Uzun çalışma saatleri arasında eğlenceli ve hareketli bir mola vererek kan dolaşımını hızlandırır.

## 🌟 Sürüm v1.0 Yenilikleri (Gold Master)
Projenin final sürümüyle eklenen profesyonel özellikler:

* **AR (Artırılmış Gerçeklik) Göstergeler:** Oyuncunun omuzları üzerinde, kolların açısını anlık gösteren dijital veriler.
* **Kalıcı Rekor Sistemi:** Oyun kapatılsa bile en yüksek skor (`rekor.txt`) hafızada tutulur.
* **Optimize Edilmiş Çizim:** Görüntü kirliliğini önlemek için sadece üst gövde (yeşil çizgilerle) çizilir.
* **Gelişmiş Arayüz:** Başlangıç menüsü, görsel uyarılar ve detaylı "Uçuş Raporu" ekranı.

## 🎮 Oynanış ve Kontroller
1.  **Menü:** "OYUNA BAŞLA" butonuna tıklayın.
2.  **Hazırlık:** Kamera karşısına geçin ve kollarınızı yana açın (T-Pose).
3.  **Kontrol Mekanizması:**
    * **Sağa Dönüş:** Sağ kolunuzu yukarı kaldırın (Açı > 130°).
    * **Sola Dönüş:** Sol kolunuzu yukarı kaldırın (Açı > 130°).
    * **⚠️ Kritik Uyarı:** Kollarınızı aşağı indirirseniz uçak irtifa kaybeder ve düşer! (Bu mekanizma oyuncuyu kolları havada tutmaya, yani spora zorlar).

## 🛠️ Kullanılan Teknolojiler
Bu proje **Görsel Programlama** dersi kapsamında aşağıdaki kütüphaneler kullanılarak hazırlanmıştır:

* **Python 3.x:** Ana programlama dili.
* **OpenCV:** Kamera görüntüsü işleme ve AR çizimleri.
* **MediaPipe:** Yapay zeka destekli iskelet ve pozisyon algılama.
* **Pygame:** Oyun motoru, grafik arayüz (UI) ve ses yönetimi.
* **NumPy:** Vücut açılarının trigonometrik hesaplamaları.

## 🚀 Kurulum
1.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install opencv-python mediapipe pygame numpy
    ```
2.  Oyunu başlatın:
    ```bash
    python main.py
    ```

---
*Görsel Programlama Dersi Final Projesidir.*