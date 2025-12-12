import cv2
import mediapipe as mp
import numpy as np
import pygame
import random
import sys

# --- 1. AYARLAR VE SABİTLER ---
EKRAN_GENISLIK = 400
EKRAN_YUKSEKLIK = 750
UCAK_HIZI = 10
KUS_HIZI = 8
T_POSE_SURESI = 20
KRITIK_SURE = 90  # 3 Saniye (30 FPS x 3)
skor = 0
en_yuksek_skor = 0

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
# Arka planın dikey konumu (Y ekseni)
arkaplan_y = 0 

# Durumlar
oyun_durumu = "BEKLEME" 
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
        sol_omuz = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        sol_dirsek = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        sol_kalca = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        sag_omuz = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        sag_dirsek = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        sag_kalca = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        
        sol_aci = calculate_angle(sol_kalca, sol_omuz, sol_dirsek)
        sag_aci = calculate_angle(sag_kalca, sag_omuz, sag_dirsek)
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
    # --- OYUN MANTIĞI ---
    
    if oyun_durumu == "BEKLEME":
        if (75 < sol_aci < 115) and (75 < sag_aci < 115):
            oyun_durumu = "UYARI"
            uyari_sayaci = 0

    elif oyun_durumu == "UYARI":
        if not ((70 < sol_aci < 120) and (70 < sag_aci < 120)):
            oyun_durumu = "BEKLEME"
        uyari_sayaci += 1
        if uyari_sayaci > 60: 
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
        # Arka planı aşağı doğru kaydır (Kuşlardan biraz daha yavaş aksın, derinlik katar)
        arkaplan_y += guncel_akis_hizi // 2 
        
        # Eğer arka plan tamamen aşağı indiyse başa sar
        if arkaplan_y >= EKRAN_YUKSEKLIK:
            arkaplan_y = 0

        # Kritik Düşüş Kontrolü
        if sol_aci < 60 or sag_aci < 60:
            dusuk_kol_sayaci += 1
            if dusuk_kol_sayaci > KRITIK_SURE:
                oyun_durumu = "BITTI"
                bitis_sebebi = "UCAK CAKILDI!"
                if skor > en_yuksek_skor:
                    en_yuksek_skor = skor
        else:
            dusuk_kol_sayaci = 0
            if sag_aci > 130: 
                ucak_x += UCAK_HIZI
            elif sol_aci > 130: 
                ucak_x -= UCAK_HIZI

    # --- EKRAN ÇİZİMLERİ ---
    
    # 1. ARKA PLAN ÇİZİMİ (SONSUZ DÖNGÜ)
    if resimler_yuklendi:
        # Birinci kopyayı çiz
        oyun_ekrani.blit(arkaplan_resmi, (0, arkaplan_y))
        # İkinci kopyayı (boşluk kalmasın diye) hemen üstüne çiz
        oyun_ekrani.blit(arkaplan_resmi, (0, arkaplan_y - EKRAN_YUKSEKLIK))
    else:
        oyun_ekrani.fill(MAVI)

    # 2. DİĞER ÇİZİMLER
    if oyun_durumu == "BEKLEME":
        yazi = font_kucuk.render("Oyuna baslamak icin", True, SIYAH)
        yazi2 = font_kucuk.render("iki kollari yana aciniz", True, SIYAH)
        oyun_ekrani.blit(yazi, (EKRAN_GENISLIK//2 - yazi.get_width()//2, EKRAN_YUKSEKLIK//2 - 50))
        oyun_ekrani.blit(yazi2, (EKRAN_GENISLIK//2 - yazi2.get_width()//2, EKRAN_YUKSEKLIK//2))

    elif oyun_durumu == "UYARI":
        if uyari_sayaci % 10 < 5: 
            t1 = font_orta.render("UNUTMAYIN!", True, KIRMIZI)
            t2 = font_kucuk.render("KOLLARINIZI INDIRIRSENIZ", True, KIRMIZI)
            t3 = font_kucuk.render("UCAK DUSER!", True, KIRMIZI)
            oyun_ekrani.blit(t1, (EKRAN_GENISLIK//2 - t1.get_width()//2, 200))
            oyun_ekrani.blit(t2, (EKRAN_GENISLIK//2 - t2.get_width()//2, 250))
            oyun_ekrani.blit(t3, (EKRAN_GENISLIK//2 - t3.get_width()//2, 280))

    elif oyun_durumu == "SAYAC":
        kalan = T_POSE_SURESI - t_pose_sayaci
        yazi = font_buyuk.render(f"HAZIRLAN...", True, YESIL)
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
            uyari_metni = font_orta.render("UCAK DUSUYOR!", True, KIRMIZI)
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
                bitis_sebebi = "CARPISMA!"
                if skor > en_yuksek_skor:
                    en_yuksek_skor = skor
            
            if kus.y > EKRAN_YUKSEKLIK:
                kus_listesi.remove(kus)
                skor += 1
        
        skor_yazi = font_orta.render(f"Skor: {skor}", True, BEYAZ)
        oyun_ekrani.blit(skor_yazi, (10, 10))

    elif oyun_durumu == "BITTI":
        yazi1 = font_buyuk.render("OYUN BITTI!", True, KIRMIZI)
        sebep_yazi = font_orta.render(bitis_sebebi, True, SIYAH)
        en_iyi_yazi = font_orta.render(f"En Iyi Skor: {en_yuksek_skor}", True, YESIL)
        yazi2 = font_orta.render(f"Skor: {skor}", True, SIYAH)
        oyun_ekrani.blit(yazi1, (EKRAN_GENISLIK//2 - yazi1.get_width()//2, 150))
        oyun_ekrani.blit(sebep_yazi, (EKRAN_GENISLIK//2 - sebep_yazi.get_width()//2, 210))
        oyun_ekrani.blit(en_iyi_yazi, (EKRAN_GENISLIK//2 - en_iyi_yazi.get_width()//2, 270))
        oyun_ekrani.blit(yazi2, (EKRAN_GENISLIK//2 - yazi2.get_width()//2, 320))
        mouse_pos = pygame.mouse.get_pos() 
        click = pygame.mouse.get_pressed() 
        buton_rect = pygame.Rect(EKRAN_GENISLIK//2 - 100, 400, 200, 60)
        if buton_rect.collidepoint(mouse_pos):
            pygame.draw.rect(oyun_ekrani, (0, 200, 0), buton_rect) 
            if click[0] == 1: 
                oyun_durumu = "BEKLEME"
                kus_listesi = []
                ucak_x = EKRAN_GENISLIK // 2 - 35 
                dusuk_kol_sayaci = 0
                arkaplan_y = 0 # Arka planı da sıfırla
        else:
            pygame.draw.rect(oyun_ekrani, YESIL, buton_rect) 
        buton_yazi = font_orta.render("TEKRAR OYNA", True, BEYAZ)
        yazi_x = buton_rect.x + (buton_rect.width - buton_yazi.get_width()) // 2
        yazi_y = buton_rect.y + (buton_rect.height - buton_yazi.get_height()) // 2
        oyun_ekrani.blit(buton_yazi, (yazi_x, yazi_y))
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