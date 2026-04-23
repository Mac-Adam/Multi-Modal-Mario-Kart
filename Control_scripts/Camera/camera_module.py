import os
import cv2
import numpy as np
import math
import time
import socket

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from mediapipe import Image
from mediapipe import ImageFormat

# Match your Unreal Engine settings
UDP_IP = "127.0.0.1"
UDP_PORT = 8001

print(f"Connecting to Unreal Engine on {UDP_IP}:{UDP_PORT}...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

MAX_ANGLE = 60
prev_time = 0
steer_filtered = 0.0

# -----------------------------
# NEW MEDIAPIPE TASKS API
# -----------------------------
# model_path = python.BaseOptions(model_asset_path="hand_landmarker.task")
script_dir = os.path.dirname(os.path.abspath(__file__))
model_file = os.path.join(script_dir, "hand_landmarker.task")

model_path = python.BaseOptions(model_asset_path=model_file)


options = vision.HandLandmarkerOptions(
    base_options=model_path,
    num_hands=2,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)

hand_landmarker = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Convert to MP Image
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = Image(image_format=ImageFormat.SRGB, data=rgb_frame)

    results = hand_landmarker.detect(mp_image)

    steer = 0.0

    if results.hand_landmarks and len(results.hand_landmarks) == 2:
        p1 = results.hand_landmarks[0][0]
        p2 = results.hand_landmarks[1][0]

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

        steer_filtered = np.round(0.3 * steer_filtered + 0.7 * steer, 1)

    else:
        steer_filtered *= 0.99

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
    prev_time = curr_time

    cv2.putText(
        frame, f"FPS:{int(fps)}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
    )

    cv2.putText(
        frame,
        f"Steer:{steer_filtered:.2f}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )

    cv2.imshow("Steering Detection", frame)

    sock.sendto(f"STEER:{steer_filtered}".encode("utf-8"), (UDP_IP, UDP_PORT))
    # time.sleep(0.016)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
sock.close()
