import cv2
import mediapipe as mp
import numpy as np
import math
import time

import socket

# Match your Unreal Engine settings
UDP_IP = "127.0.0.1"
UDP_PORT = 8001

print(f"Connecting to Unreal Engine on {UDP_IP}:{UDP_PORT}...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

MAX_ANGLE = 60  # Maksymalny kąt, który odpowiada pełnemu skrętowi (1.0 lub -1.0)

prev_time = 0
steer_filtered = 0.0

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    h, w, _ = frame.shape

    steer = 0.0

    if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:

        p1 = results.multi_hand_landmarks[0].landmark[0]
        p2 = results.multi_hand_landmarks[1].landmark[0]

        x1, y1 = int(p1.x * w), int(p1.y * h)
        x2, y2 = int(p2.x * w), int(p2.y * h)

        cv2.circle(frame, (x1, y1), 10, (255, 0, 0), -1)
        cv2.circle(frame, (x2, y2), 10, (255, 0, 0), -1)

        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

        dx = x2 - x1
        dy = y2 - y1

        angle = math.degrees(math.atan2(dy, dx))

        if angle < -90 or angle > 90:
            angle = math.degrees(math.atan2(-dy, -dx))

        steer = angle / MAX_ANGLE

        steer = max(-1, min(1, steer))

        # low-pass filter
        steer_filtered = np.round(0.3 * steer_filtered + 0.7 * steer, 1)

    else:
        steer_filtered *= 0.9

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
    prev_time = curr_time

    cv2.putText(
        frame, f"FPS:{int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
    )

    cv2.putText(
        frame,
        f"Steer:{steer_filtered:.2f}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )

    cv2.imshow("Steering Detection", frame)

    # Send the packets
    sock.sendto(f"STEER:{steer_filtered}".encode("utf-8"), (UDP_IP, UDP_PORT))

    # Sleep for 16 milliseconds to send data at roughly 60 Frames Per Second
    time.sleep(0.016)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
sock.close()
