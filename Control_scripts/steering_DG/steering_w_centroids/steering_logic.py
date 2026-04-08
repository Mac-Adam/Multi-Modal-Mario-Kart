import cv2
import numpy as np
import math

def get_centroid(cnt):
    """Wylicza środek ciężkości konturu."""
    M = cv2.moments(cnt)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        return (cx, cy)
    return None

def process_frame(frame, lower_color, upper_color, min_area, max_steer_angle=80):
    """
    Analizuje klatkę pod kątem dwóch punktów ciężkości.
    Zwraca: (surowy_skręt, maska, klatka_z_wizualizacją)
    """
    # 1. Preprocessing (CIELAB)
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2Lab)
    mask = cv2.inRange(lab, lower_color, upper_color)
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # 2. Szukanie konturów
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]

    centroids = []
    for cnt in sorted_contours:
        if cv2.contourArea(cnt) > min_area:
            pos = get_centroid(cnt)
            if pos:
                centroids.append(pos)
                cv2.circle(frame, pos, 10, (0, 255, 0), -1)

    # 3. Obliczanie kąta między punktami
    steer_val = 0.0
    if len(centroids) == 2:
        # Sortowanie po X (lewa ręka, prawa ręka)
        centroids = sorted(centroids, key=lambda p: p[0])
        p1, p2 = centroids[0], centroids[1]
        
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        
        angle_deg = math.degrees(math.atan2(dy, dx))
        
        # Normalizacja do zakresu -1.0 ; 1.0
        normalized = angle_deg / max_steer_angle
        steer_val = max(-1.0, min(1.0, normalized))
        
        # Rysowanie linii łączącej
        cv2.line(frame, p1, p2, (255, 0, 0), 3)

    return round(steer_val, 3), mask, frame
