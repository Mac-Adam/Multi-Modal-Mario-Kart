import cv2
import numpy as np
import math


def get_mask(frame, lower_color, upper_color):
    """Konwertuje obraz do CIELAB i nakłada maskę."""
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2Lab)
    mask = cv2.inRange(lab, lower_color, upper_color)
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)


def get_arrow_steering(cnt, max_angle=80):
    """Oblicza znormalizowany kąt skrętu z pojedynczego konturu."""
    # [vx, vy, x, y] = cv2.fitLine(cnt, cv2.DIST_L2, 0, 0.01, 0.01)
    # fixes
    vx, vy, x, y = cv2.fitLine(cnt, cv2.DIST_L2, 0, 0.01, 0.01).reshape(-1)
    vx, vy, x, y = float(vx), float(vy), float(x), float(y)

    angle_rad = math.atan2(vy, vx)
    angle_deg = math.degrees(angle_rad)

    # Normalizacja: pion = 0 stopni
    steer_angle = angle_deg + 90 if angle_deg < 0 else angle_deg - 90
    normalized = steer_angle / max_angle
    return max(-1.0, min(1.0, normalized)), (int(x), int(y)), (vx, vy)


def process_frame(frame, lower_color, upper_color, min_area):
    """Główna funkcja procesująca klatkę. Zwraca finalny steer i obraz do wyświetlenia."""
    mask = get_mask(frame, lower_color, upper_color)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]

    angles = []
    for cnt in sorted_contours:
        if cv2.contourArea(cnt) > min_area:
            steer_val, center, _ = get_arrow_steering(cnt)
            angles.append(steer_val)
            # Rysowanie punktu na klatce
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

    final_steer = np.mean(angles) if angles else 0.0
    return round(final_steer, 3), mask, frame
