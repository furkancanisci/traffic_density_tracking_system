import cv2
import numpy as np
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk

# --- 1. AYARLAR ---
VIDEO_SOURCE = 'traffic.mp4'
MIN_CONTOUR_AREA = 60         # Çok küçük noktaları almasın (40'tan 60'a çıkardım)
WINDOW_SIZE = (1280, 760)
GRID_SIZE = (640, 360)

# --- 2. DEĞİŞKENLER ---
is_running = False

# --- 3. ARAYÜZ KURULUMU ---
root = tk.Tk()
root.title("Trafik Analizi - Akıllı Araç Filtreleme")
root.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
root.configure(bg="#20232a")

main_label = Label(root, bg="#20232a")
main_label.pack(expand=True, fill="both")

# --- 4. OPENCV NESNELERİ ---
cap = cv2.VideoCapture(VIDEO_SOURCE)

# ÖNEMLİ AYAR: varThreshold
# Bu değeri 50'den 100'e çıkardık. 
# Bu sayede şeritler gibi hafif renk değişimlerini değil, sadece araçları algılar.
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=250, detectShadows=True)

def toggle_simulation():
    global is_running
    if is_running:
        is_running = False
        btn_action.config(text="Sistemi BAŞLAT", bg="#27ae60", fg="white")
    else:
        is_running = True
        btn_action.config(text="Sistemi DURDUR", bg="#c0392b", fg="white")
        update_ui()

def update_ui():
    global is_running
    if not is_running:
        return

    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()

    # --- GÖRÜNTÜ İŞLEME ---
    frame_resized = cv2.resize(frame, GRID_SIZE)
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
    
    # Blur miktarını biraz artırdım (Gürültüyü azaltmak için)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 1. Arka Plan Çıkarma
    mask = bg_subtractor.apply(blur)
    
    # 2. Maske Temizleme
    # Threshold değerini 240 yaparak sadece en parlak hareketleri alıyoruz
    _, mask_clean = cv2.threshold(mask, 240, 255, cv2.THRESH_BINARY)
    
    # Genişletme (Dilation) işlemini biraz kıstık (Çok birleşmesinler diye)
    kernel = np.ones((3, 3), np.uint8)
    mask_clean = cv2.dilate(mask_clean, kernel, iterations=1) # 2'den 1'e düşürdüm, daha net olsun

    # 3. Kontur Bulma
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    result_frame = frame_resized.copy()
    current_cars_on_screen = 0

    for c in contours:
        area = cv2.contourArea(c)
        
        # 1. Alan Filtresi: Çok küçükleri atla
        if area < MIN_CONTOUR_AREA:
            continue 

        # 2. GEOMETRİK FİLTRE (YENİ ÖZELLİK)
        # Aracın en-boy oranına bakarak şerit mi araba mı olduğuna karar veriyoruz
        (x, y, w, h) = cv2.boundingRect(c)
        aspect_ratio = float(w) / h
        
        # Arabalar genellikle kareye yakındır (Oran 0.5 ile 2.5 arası)
        # Eğer oran 4.0 ise bu ince uzun bir şerittir, atla.
        # Eğer oran 0.1 ise bu dikey bir direktir, atla.
        if aspect_ratio > 3.0 or aspect_ratio < 0.3:
            continue

        current_cars_on_screen += 1
        
        # Kutuyu çiz
        cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # --- GÖRSELLEŞTİRME ---
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    mask_clean_bgr = cv2.cvtColor(mask_clean, cv2.COLOR_GRAY2BGR)

    cv2.putText(frame_resized, "1. Kaynak", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(mask_bgr, "2. MOG2 (Hassas)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(mask_clean_bgr, "3. Filtrelenmis Maske", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(result_frame, f"ARAC SAYISI: {current_cars_on_screen}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    top_row = np.hstack([frame_resized, mask_bgr])
    bottom_row = np.hstack([mask_clean_bgr, result_frame])
    final_grid = np.vstack([top_row, bottom_row])

    img_rgb = cv2.cvtColor(final_grid, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)

    main_label.imgtk = img_tk
    main_label.configure(image=img_tk)
    
    root.after(10, update_ui)

# --- BUTON ---
btn_action = Button(root, text="Sistemi BAŞLAT", font=("Arial", 14, "bold"), 
                    bg="#27ae60", fg="white", height=2, command=toggle_simulation)
btn_action.pack(side="bottom", fill="x", padx=20, pady=20)

root.mainloop()