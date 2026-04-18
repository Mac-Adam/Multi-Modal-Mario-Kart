import cv2
import socket
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from steering_logic import process_frame
from connection_settings import load_config

# --- KONFIGURACJA ---
config = load_config()
UDP_IP = config.get("udp_ip", config.get("host", "127.0.0.1"))
UDP_PORT = config.get("udp_port", 8001)
LOWER_COLOR = np.array([50, 80, 50])   # Przykładowe dla błękitu
UPPER_COLOR = np.array([255, 125, 115])
MIN_AREA = 400

# --- WYGŁADZANIE STEROWANIA ---
smoothed_steer = 0.0
alpha = 0.2  # Im mniejszy, tym płynniej, ale z większym opóźnieniem

# Inicjalizacja sieci
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cap = cv2.VideoCapture(0)

print("System uruchomiony. Naciśnij 'q' aby wyjść.")

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)

    # Wykorzystanie logiki z drugiego pliku
    steer_val, mask, debug_frame = process_frame(frame, LOWER_COLOR, UPPER_COLOR, MIN_AREA)

    # Wysyłka UDP
    # Wersja z wygładzaniem:
    smoothed_steer = (alpha * steer_val) + ((1 - alpha) * smoothed_steer)
    # message = f"STEER:{smoothed_steer:.3f}"
    # Wersja bez wygładzania:
    message = f"STEER:{steer_val}"
    sock.sendto(message.encode("utf-8"), (UDP_IP, UDP_PORT))

    # 4. Wizualizacja (Collage)
# !!!UWAGA!!! - po testach zakomentować, by przyspieszyć działanie
    mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    collage = np.hstack((debug_frame, mask_3ch))
    
    cv2.putText(collage, f"RAW: {steer_val}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(collage, f"SMOOTH: {smoothed_steer:.3f}", (20, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    cv2.imshow("Sterowanie - Podgląd", collage)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
sock.close()
