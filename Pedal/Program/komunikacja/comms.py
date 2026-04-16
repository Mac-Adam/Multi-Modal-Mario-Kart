# PLIK ODCZYTUJĄCY DANE Z SERIAL I PRZESYŁAJĄCE JE PO UDP

import serial
import socket

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
UDP_IP, UDP_PORT = "127.0.0.1", 8001
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