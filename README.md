# AI Motion Controlled Flight Game ✈️

Bu proje, Python kullanılarak geliştirilmiş, vücut hareketleriyle kontrol edilen bir uçuş simülasyonu oyunudur. MediaPipe kütüphanesi ile oyuncunun kolları ve vücut pozisyonu algılanır; bu hareketler uçağın kontrolünü sağlar. Bu sayede ise hem egzersiz yapıp hemde eğlenerek oyun oynamış oluruz.

## 🎮 Özellikler
* **Gerçek Zamanlı Vücut Takibi:** Kamera üzerinden kolların açısını hesaplar.
* **T-Pose Başlangıcı:** Oyunu başlatmak için kalibrasyon hareketi.
* **Exergame Mantığı:** Kollarınızı indirirseniz uçak alçalır ve düşer!
* **Sonsuz Akış:** Arka plan ve engeller sürekli akar.
* **Dinamik Zorluk:** Skor arttıkça oyun hızlanır.

## 🛠️ Kullanılan Teknolojiler
* Python 3.11
* OpenCV (Görüntü İşleme)
* MediaPipe (Pose Estimation)
* Pygame (Oyun Motoru)

## 🚀 Kurulum ve Çalıştırma
1. Projeyi indirin.
2. Gerekli kütüphaneleri kurun:
   `pip install -r requirements.txt`
3. Oyunu başlatın:
   `python main.py`
