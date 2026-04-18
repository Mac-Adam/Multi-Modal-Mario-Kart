# PLIK ODCZYTUJĄCY DANE Z SERIAL I PRZESYŁAJĄCE JE PO UDP

import serial
import socket
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from connection_settings import load_config

config = load_config()
UDP_IP = config.get("udp_ip", config.get("host", "127.0.0.1"))
UDP_PORT = config.get("udp_port", 8001)

# --- KONFIGURACJA SERIAL ---
port = 'COM3' # DOPASOWAĆ DO SWOJEGO PORTU
serialInst = serial.Serial()
serialInst.baudrate = 115200
serialInst.port = port
serialInst.bytesize = 8
serialInst.parity = serial.PARITY_NONE
serialInst.stopbits = 1
serialInst.open()

# --- KONFIGURACJA UDP ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Połączono z {port}. Przesyłanie danych do UE5 na {UDP_IP}:{UDP_PORT}...")

try:
    while True:
        if serialInst.in_waiting:
            # Odczytujemy linię z Serial Portu
            packet = serialInst.readline()
            data = packet.decode('utf-8', errors='ignore').strip()
            
            if data:
                try:
                    # Konwersja na float
                    throttle = float(data)
                    print(f"Throttle: {throttle:>6.2f}")
                    
                    # Wysyłka UDP do Unreal Engine
                    message = f"STEER:{throttle}"
                    sock.sendto(message.encode("utf-8"), (UDP_IP, UDP_PORT))
                    
                except ValueError:
                    print(f"Odebrano tekst: {data}")

except KeyboardInterrupt:
    print("\nZakończono odczyt.")
    serialInst.close()
    sock.close()