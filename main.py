import cv2
import mediapipe as mp
import numpy as np
import pygame
import random
import sys
import os # Dosya işlemleri için gerekli

# --- 1. AYARLAR VE SABİTLER ---
EKRAN_GENISLIK = 400
EKRAN_YUKSEKLIK = 750
UCAK_HIZI = 10
KUS_HIZI = 8
T_POSE_SURESI = 20
KRITIK_SURE = 90  # 3 Saniye (30 FPS x 3)
skor = 0

# --- YENİ EKLENEN: REKOR SİSTEMİ BAŞLANGIÇ ---
# Oyun açılırken rekor dosyasını okumaya çalışır
try:
    with open("rekor.txt", "r") as dosya:
        en_yuksek_skor = int(dosya.read())
except:
    # Dosya yoksa veya hata verirse rekor 0 olsun
    en_yuksek_skor = 0
# --- REKOR SİSTEMİ BİTİŞ ---

# Renkler
BEYAZ = (255, 255, 255)
MAVI = (135, 206, 235)
KIRMIZI = (255, 0, 0)
SIYAH = (0, 0, 0)
YESIL = (0, 255, 0)
TURUNCU = (255, 165, 0)

# --- 2. FONKSİYONLAR ---
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0: angle = 360 - angle
    return angle

def rekor_kaydet(yeni_skor):
    global en_yuksek_skor
    if yeni_skor > en_yuksek_skor:
        en_yuksek_skor = yeni_skor
        # Yeni rekoru dosyaya yaz
        with open("rekor.txt", "w") as dosya:
            dosya.write(str(en_yuksek_skor))

# --- 3. BAŞLATMA ---
pygame.init()
oyun_ekrani = pygame.display.set_mode((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
pygame.display.set_caption("Ucus Simulatoru")
clock = pygame.time.Clock()

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

# Oyun Değişkenleri
ucak_genislik = 70
ucak_yukseklik = 100
ucak_x = EKRAN_GENISLIK // 2 - 35
ucak_y = EKRAN_YUKSEKLIK - 120

# --- RESİM YÜKLEME KISMI ---
try:
    # Arka Plan
    arkaplan_img_orj = pygame.image.load("arkaplan.png").convert()
    arkaplan_resmi = pygame.transform.scale(arkaplan_img_orj, (EKRAN_GENISLIK, EKRAN_YUKSEKLIK))

    # Uçak Resmi
    ucak_img_orj = pygame.image.load("ucak.png").convert_alpha()
    ucak_resmi = pygame.transform.scale(ucak_img_orj, (ucak_genislik, ucak_yukseklik))
    
    # Kuş Resmi
    kus_img_orj = pygame.image.load("kus.png").convert_alpha()
    kus_resmi = pygame.transform.scale(kus_img_orj, (40, 40)) 
    resimler_yuklendi = True
    print("Resimler başarıyla yüklendi.")
except:
    print("HATA: Resimler bulunamadı!")
    resimler_yuklendi = False


kus_listesi = []
spawn_timer = 0
skor = 0

# --- ARKA PLAN HAREKET DEĞİŞKENİ ---
arkaplan_y = 0 

# Durumlar
oyun_durumu = "MENU" 
t_pose_sayaci = 0
uyari_sayaci = 0        
dusuk_kol_sayaci = 0  
bitis_sebebi = ""

# Fontlar
font_buyuk = pygame.font.Font(None, 50)
font_orta = pygame.font.Font(None, 36)
font_kucuk = pygame.font.Font(None, 24)

print("Sistem Hazir. Baslatiliyor...")

# --- 4. ANA DÖNGÜ ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release(); cv2.destroyAllWindows(); pygame.quit(); sys.exit()

    ret, frame = cap.read()
    if not ret: continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    
    sol_aci = 0
    sag_aci = 0
    
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        
        # Koordinatları al
        sol_omuz = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        sol_dirsek = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        sol_kalca = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        sag_omuz = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        sag_dirsek = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        sag_kalca = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        
        # Açıları hesapla
        sol_aci = calculate_angle(sol_kalca, sol_omuz, sol_dirsek)
        sag_aci = calculate_angle(sag_kalca, sag_omuz, sag_dirsek)
        
        # --- ÖZEL İSKELET ÇİZİMİ (Sadece Üst Vücut) ---
        
        # Ekran boyutlarını al
        h, w, _ = frame.shape
        
        # Koordinatları piksele çeviren yardımcı kısa fonksiyon
        get_px = lambda lm: (int(lm.x * w), int(lm.y * h))

        # Gerekli noktaları al
        lm = results.pose_landmarks.landmark
        p_sol_omuz = get_px(lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value])
        p_sol_dirsek = get_px(lm[mp_pose.PoseLandmark.LEFT_ELBOW.value])
        p_sol_bilek = get_px(lm[mp_pose.PoseLandmark.LEFT_WRIST.value])
        p_sol_kalca = get_px(lm[mp_pose.PoseLandmark.LEFT_HIP.value])
        
        p_sag_omuz = get_px(lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value])
        p_sag_dirsek = get_px(lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value])
        p_sag_bilek = get_px(lm[mp_pose.PoseLandmark.RIGHT_WRIST.value])
        p_sag_kalca = get_px(lm[mp_pose.PoseLandmark.RIGHT_HIP.value])

        # ÇİZGİLERİ ÇİZ (Kalınlık: 3, Renk: Yeşil)
        cv2.line(frame, p_sol_omuz, p_sol_dirsek, (0, 255, 0), 3)
        cv2.line(frame, p_sol_dirsek, p_sol_bilek, (0, 255, 0), 3)
        cv2.line(frame, p_sag_omuz, p_sag_dirsek, (0, 255, 0), 3)
        cv2.line(frame, p_sag_dirsek, p_sag_bilek, (0, 255, 0), 3)
        cv2.line(frame, p_sol_omuz, p_sag_omuz, (0, 255, 0), 3) 
        cv2.line(frame, p_sol_omuz, p_sol_kalca, (0, 255, 0), 3) 
        cv2.line(frame, p_sag_omuz, p_sag_kalca, (0, 255, 0), 3) 
        cv2.line(frame, p_sol_kalca, p_sag_kalca, (0, 255, 0), 3) 

        # NOKTALARI KOY 
        noktalar = [p_sol_omuz, p_sol_dirsek, p_sol_bilek, p_sol_kalca, 
                   p_sag_omuz, p_sag_dirsek, p_sag_bilek, p_sag_kalca]
        
        for nokta in noktalar:
            cv2.circle(frame, nokta, 5, (0, 0, 255), -1) 

        # AÇILARI EKRANA YAZDIRMA
        text_x_sol = int(sol_omuz[0] * w)
        text_y_sol = int(sol_omuz[1] * h)
        text_x_sag = int(sag_omuz[0] * w)
        text_y_sag = int(sag_omuz[1] * h)

        cv2.putText(frame, str(int(sol_aci)), (text_x_sol + 10, text_y_sol - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(frame, str(int(sol_aci)), (text_x_sol + 10, text_y_sol - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.putText(frame, str(int(sag_aci)), (text_x_sag - 60, text_y_sag - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(frame, str(int(sag_aci)), (text_x_sag - 60, text_y_sag - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
    # --- OYUN MANTIĞI ---
    
    if oyun_durumu == "BEKLEME":
        if (75 < sol_aci < 115) and (75 < sag_aci < 115):
            oyun_durumu = "UYARI"
            uyari_sayaci = 0

    elif oyun_durumu == "UYARI":
        if not ((70 < sol_aci < 120) and (70 < sag_aci < 120)):
            oyun_durumu = "BEKLEME"
        uyari_sayaci += 1
        if uyari_sayaci > 90: 
            oyun_durumu = "SAYAC"
            t_pose_sayaci = 0

    elif oyun_durumu == "SAYAC":
        if (70 < sol_aci < 120) and (70 < sag_aci < 120):
            t_pose_sayaci += 1
            if t_pose_sayaci > T_POSE_SURESI:
                oyun_durumu = "OYUN"
                skor = 0
                kus_listesi = []
                dusuk_kol_sayaci = 0 
        else:
            oyun_durumu = "BEKLEME" 

    elif oyun_durumu == "OYUN":
        
        # Akış Hızı Hesaplama
        guncel_akis_hizi = int(KUS_HIZI * (1 + (skor // 10) * 0.2))

        # --- ARKA PLAN HAREKETİ ---
        arkaplan_y += guncel_akis_hizi // 2 
        if arkaplan_y >= EKRAN_YUKSEKLIK:
            arkaplan_y = 0

        # Kritik Düşüş Kontrolü
        if sol_aci < 60 or sag_aci < 60:
            dusuk_kol_sayaci += 1
            if dusuk_kol_sayaci > KRITIK_SURE:
                oyun_durumu = "BITTI"
                bitis_sebebi = "UÇAK ÇAKILDI!"
                rekor_kaydet(skor) # REKORU KAYDET
        else:
            dusuk_kol_sayaci = 0
            if sag_aci > 130: 
                ucak_x += UCAK_HIZI
            elif sol_aci > 130: 
                ucak_x -= UCAK_HIZI

    # --- EKRAN ÇİZİMLERİ ---
    
    if resimler_yuklendi:
        oyun_ekrani.blit(arkaplan_resmi, (0, arkaplan_y))
        oyun_ekrani.blit(arkaplan_resmi, (0, arkaplan_y - EKRAN_YUKSEKLIK))
    else:
        oyun_ekrani.fill(MAVI)

    if oyun_durumu == "MENU":
        baslik = font_buyuk.render("UÇUŞ SİMULATORÜ", True, SIYAH)
        oyun_ekrani.blit(baslik, (EKRAN_GENISLIK//2 - baslik.get_width()//2, 150))

        mouse_pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        buton_rect = pygame.Rect(EKRAN_GENISLIK//2 - 100, 350, 200, 60)

        if buton_rect.collidepoint(mouse_pos):
            pygame.draw.rect(oyun_ekrani, (0, 200, 0), buton_rect) 
            if click[0] == 1: 
                oyun_durumu = "BEKLEME" 
        else:
            pygame.draw.rect(oyun_ekrani, YESIL, buton_rect) 

        buton_yazi = font_orta.render("OYUNA BAŞLA", True, BEYAZ)
        yazi_x = buton_rect.x + (buton_rect.width - buton_yazi.get_width()) // 2
        yazi_y = buton_rect.y + (buton_rect.height - buton_yazi.get_height()) // 2
        oyun_ekrani.blit(buton_yazi, (yazi_x, yazi_y))

        # (REKOR GÖSTERGESİ)
        rekor_str = f"En Yüksek Skor: {en_yuksek_skor}"
        rekor_yazi = font_kucuk.render(rekor_str, True, KIRMIZI) 
        
        # Yazıyı ortala ve çiz
        rekor_x = EKRAN_GENISLIK // 2 - rekor_yazi.get_width() // 2
        oyun_ekrani.blit(rekor_yazi, (rekor_x, 430))


    elif oyun_durumu == "BEKLEME":
        kutu_genislik = 320
        kutu_yukseklik = 180 
        kutu_x = EKRAN_GENISLIK // 2 - kutu_genislik // 2
        kutu_y = EKRAN_YUKSEKLIK // 2 - 100 
        
        uyari_kutusu = pygame.Surface((kutu_genislik, kutu_yukseklik))
        uyari_kutusu.set_alpha(180) 
        uyari_kutusu.fill(SIYAH)    
        
        oyun_ekrani.blit(uyari_kutusu, (kutu_x, kutu_y))
        pygame.draw.rect(oyun_ekrani, BEYAZ, (kutu_x, kutu_y, kutu_genislik, kutu_yukseklik), 3)

        baslik_yazi = font_orta.render("HAZIRLAN", True, YESIL) 
        talimat1 = font_kucuk.render("Oyuna başlamak için", True, BEYAZ) 
        talimat2 = font_kucuk.render("iki kolunuzu dümdüz olacak şekilde", True, BEYAZ)
        talimat3 = font_kucuk.render("yanlara açınız (90°)", True, BEYAZ) 

        baslik_x = kutu_x + (kutu_genislik - baslik_yazi.get_width()) // 2
        oyun_ekrani.blit(baslik_yazi, (baslik_x, kutu_y + 20))
        talimat1_x = kutu_x + (kutu_genislik - talimat1.get_width()) // 2
        oyun_ekrani.blit(talimat1, (talimat1_x, kutu_y + 60))
        talimat2_x = kutu_x + (kutu_genislik - talimat2.get_width()) // 2
        oyun_ekrani.blit(talimat2, (talimat2_x, kutu_y + 90))
        talimat3_x = kutu_x + (kutu_genislik - talimat3.get_width()) // 2
        oyun_ekrani.blit(talimat3, (talimat3_x, kutu_y + 120)) 

    elif oyun_durumu == "UYARI":
        kutu_genislik = 340
        kutu_yukseklik = 160
        kutu_x = EKRAN_GENISLIK // 2 - kutu_genislik // 2
        kutu_y = EKRAN_YUKSEKLIK // 2 - 100

        uyari_kutusu = pygame.Surface((kutu_genislik, kutu_yukseklik))
        uyari_kutusu.set_alpha(210)  
        uyari_kutusu.fill((50, 0, 0)) 
        oyun_ekrani.blit(uyari_kutusu, (kutu_x, kutu_y))

        if uyari_sayaci % 55 < 40:
            pygame.draw.rect(oyun_ekrani, KIRMIZI, (kutu_x, kutu_y, kutu_genislik, kutu_yukseklik), 4)
            baslik = font_orta.render("! DİKKAT !", True, KIRMIZI)
            t1 = font_kucuk.render("Kollarınızı indirirseniz", True, BEYAZ)
            t2 = font_kucuk.render("dengenizi kaybedersiniz ve", True, BEYAZ)
            t3 = font_kucuk.render("uçak düşer !", True, BEYAZ) 

            oyun_ekrani.blit(baslik, (kutu_x + (kutu_genislik - baslik.get_width())//2, kutu_y + 20))
            oyun_ekrani.blit(t1, (kutu_x + (kutu_genislik - t1.get_width())//2, kutu_y + 60))
            oyun_ekrani.blit(t2, (kutu_x + (kutu_genislik - t2.get_width())//2, kutu_y + 90))
            oyun_ekrani.blit(t3, (kutu_x + (kutu_genislik - t3.get_width())//2, kutu_y + 120))
        else:
            pygame.draw.rect(oyun_ekrani, (100, 0, 0), (kutu_x, kutu_y, kutu_genislik, kutu_yukseklik), 2)

    elif oyun_durumu == "SAYAC":
        kalan = T_POSE_SURESI - t_pose_sayaci
        yazi = font_buyuk.render(f"BAŞLIYOR...", True, SIYAH)
        cubuk_uzunluk = int((t_pose_sayaci / T_POSE_SURESI) * 200)
        pygame.draw.rect(oyun_ekrani, YESIL, (100, 400, cubuk_uzunluk, 30))
        pygame.draw.rect(oyun_ekrani, SIYAH, (100, 400, 200, 30), 2)
        oyun_ekrani.blit(yazi, (EKRAN_GENISLIK//2 - yazi.get_width()//2, 300))

    elif oyun_durumu == "OYUN":
        if ucak_x < 0: ucak_x = 0
        if ucak_x > EKRAN_GENISLIK - ucak_genislik: ucak_x = EKRAN_GENISLIK - ucak_genislik

        titreme_x = 0
        if dusuk_kol_sayaci > 0:
            titreme_x = random.randint(-5, 5)

        ucak_rect = pygame.Rect(ucak_x + titreme_x, ucak_y, ucak_genislik, ucak_yukseklik)
        
        if resimler_yuklendi:
            oyun_ekrani.blit(ucak_resmi, ucak_rect)
        else:
            pygame.draw.rect(oyun_ekrani, KIRMIZI, ucak_rect)

        if dusuk_kol_sayaci > 0:
            kalan_saniye = 3 - (dusuk_kol_sayaci // 30)
            kirmizi_yuzey = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
            kirmizi_yuzey.set_alpha(50)
            kirmizi_yuzey.fill(KIRMIZI)
            oyun_ekrani.blit(kirmizi_yuzey, (0,0))
            uyari_metni = font_orta.render("UÇAK DÜŞÜYOR", True, KIRMIZI)
            uyari_metni2 = font_buyuk.render(f"{kalan_saniye}", True, KIRMIZI)
            uyari_metni3 = font_kucuk.render("KOLLARI KALDIR!", True, SIYAH)
            oyun_ekrani.blit(uyari_metni, (EKRAN_GENISLIK//2 - uyari_metni.get_width()//2, 150))
            oyun_ekrani.blit(uyari_metni2, (EKRAN_GENISLIK//2 - uyari_metni2.get_width()//2, 200))
            oyun_ekrani.blit(uyari_metni3, (EKRAN_GENISLIK//2 - uyari_metni3.get_width()//2, 250))

        spawn_timer += 1
        if spawn_timer > 30:
            kus_x = random.randint(0, EKRAN_GENISLIK - 40)
            kus_rect = pygame.Rect(kus_x, -50, 40, 40)
            kus_listesi.append(kus_rect)
            spawn_timer = 0
        
        for kus in kus_listesi[:]:
            kus.y += guncel_akis_hizi
            if resimler_yuklendi:
                oyun_ekrani.blit(kus_resmi, kus)
            else:
                pygame.draw.rect(oyun_ekrani, SIYAH, kus)
            
            if ucak_rect.inflate(-20, -15).colliderect(kus):
                oyun_durumu = "BITTI"
                bitis_sebebi = "ÇARPIŞMA!"
                rekor_kaydet(skor) # REKORU KAYDET
            
            if kus.y > EKRAN_YUKSEKLIK:
                kus_listesi.remove(kus)
                skor += 1
        
        skor_yazi = font_orta.render(f"Skor: {skor}", True, BEYAZ)
        oyun_ekrani.blit(skor_yazi, (10, 10))

    elif oyun_durumu == "BITTI":
        siyah_filtre = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
        siyah_filtre.set_alpha(150) 
        siyah_filtre.fill(SIYAH)
        oyun_ekrani.blit(siyah_filtre, (0,0))

        panel_genislik = 320
        panel_yukseklik = 400
        panel_x = EKRAN_GENISLIK // 2 - panel_genislik // 2
        panel_y = EKRAN_YUKSEKLIK // 2 - 200

        pygame.draw.rect(oyun_ekrani, (40, 40, 40), (panel_x, panel_y, panel_genislik, panel_yukseklik), border_radius=20)
        pygame.draw.rect(oyun_ekrani, BEYAZ, (panel_x, panel_y, panel_genislik, panel_yukseklik), 3, border_radius=20)

        baslik = font_buyuk.render("OYUN BİTTİ", True, KIRMIZI)
        oyun_ekrani.blit(baslik, (panel_x + (panel_genislik - baslik.get_width())//2, panel_y + 30))

        sebep = font_orta.render(bitis_sebebi, True, BEYAZ)
        oyun_ekrani.blit(sebep, (panel_x + (panel_genislik - sebep.get_width())//2, panel_y + 80))

        pygame.draw.line(oyun_ekrani, BEYAZ, (panel_x + 40, panel_y + 120), (panel_x + panel_genislik - 40, panel_y + 120), 2)

        skor_baslik = font_kucuk.render("TOPLAM SKOR", True, (200, 200, 200)) 
        skor_deger = font_buyuk.render(str(skor), True, YESIL)
        
        oyun_ekrani.blit(skor_baslik, (panel_x + (panel_genislik - skor_baslik.get_width())//2, panel_y + 140))
        oyun_ekrani.blit(skor_deger, (panel_x + (panel_genislik - skor_deger.get_width())//2, panel_y + 170))

        rekor_metni = font_kucuk.render(f"En Yüksek Skor: {en_yuksek_skor}", True, TURUNCU)
        oyun_ekrani.blit(rekor_metni, (panel_x + (panel_genislik - rekor_metni.get_width())//2, panel_y + 220))

        mouse_pos = pygame.mouse.get_pos() 
        click = pygame.mouse.get_pressed() 
        
        btn_w, btn_h = 200, 50
        btn_x = panel_x + (panel_genislik - btn_w) // 2
        btn_y = panel_y + 300
        
        buton_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        
        if buton_rect.collidepoint(mouse_pos):
            pygame.draw.rect(oyun_ekrani, (0, 200, 0), buton_rect, border_radius=10) 
            if click[0] == 1: 
                oyun_durumu = "BEKLEME"
                kus_listesi = []
                ucak_x = EKRAN_GENISLIK // 2 - 35 
                dusuk_kol_sayaci = 0
                arkaplan_y = 0 
        else:
            pygame.draw.rect(oyun_ekrani, YESIL, buton_rect, border_radius=10) 
            
        btn_yazi = font_orta.render("TEKRAR OYNA", True, BEYAZ)
        yazi_x = btn_x + (btn_w - btn_yazi.get_width()) // 2
        yazi_y = btn_y + (btn_h - btn_yazi.get_height()) // 2
        oyun_ekrani.blit(btn_yazi, (yazi_x, yazi_y))
        
        kisayol = font_kucuk.render("veya 'R' tuşuna bas", True, (150, 150, 150))
        oyun_ekrani.blit(kisayol, (panel_x + (panel_genislik - kisayol.get_width())//2, btn_y + 60))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            oyun_durumu = "BEKLEME"
            kus_listesi = []
            ucak_x = EKRAN_GENISLIK // 2 - 35
            dusuk_kol_sayaci = 0
            arkaplan_y = 0

    cv2.imshow('Kamera', frame)
    pygame.display.update()
    clock.tick(30)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()