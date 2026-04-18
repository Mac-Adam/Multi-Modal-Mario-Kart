# IMPLEMENTACJA STEROWANIA Z ESP PRZEZ SERIAL W PRZYKADOWYM PLIKU PLAYER1

import serial
import socket
import keyboard
import time
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from connection_settings import load_config

config = load_config()
UDP_IP = config.get("udp_ip", config.get("host", "127.0.0.1"))
UDP_PORT = config.get("udp_port", 8001)

# Inicjalizacja Serial
try:
    port = 'COM3' # DOPASOWAĆ DO SWOJEGO PORTU
    serialInst = serial.Serial()
    serialInst.baudrate = 115200
    serialInst.port = port
    serialInst.bytesize = 8
    serialInst.parity = serial.PARITY_NONE
    serialInst.stopbits = 1
    serialInst.open()
    print(f"Połączono z {SERIAL_PORT}. Odczyt Throttle z Serial Portu.")
except Exception as e:
    print(f"Błąd portu {SERIAL_PORT}: {e}")
    serialInst = None

# Inicjalizacja UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

current_throttle = 0.0

print("--- Kontroler Hybrydowy Aktywny ---")
print("Serial: THROTTLE | Klawiatura: A/D (Steer), SPACE (Handbrake)")

try:
    while True:
        if keyboard.is_pressed('esc'):
            break

        steer = 0.0
        handbrake = 0
        
        if keyboard.is_pressed('a'): steer = -1.0
        if keyboard.is_pressed('d'): steer = 1.0
        if keyboard.is_pressed('space'): handbrake = 1

        if serialInst and serialInst.in_waiting:
            packet = serialInst.readline()
            data = packet.decode('utf-8', errors='ignore').strip()
            try:
                current_throttle = float(data)
            except ValueError:
                pass

        sock.sendto(f"STEER:{steer}".encode('utf-8'), (UDP_IP, UDP_PORT))
        sock.sendto(f"THROTTLE:{current_throttle}".encode('utf-8'), (UDP_IP, UDP_PORT))
        sock.sendto(f"HANDBRAKE:{handbrake}".encode('utf-8'), (UDP_IP, UDP_PORT))

        time.sleep(0.016)

except KeyboardInterrupt:
    print("\nZamykanie...")
finally:
    if serialInst:
        serialInst.close()
    sock.close()