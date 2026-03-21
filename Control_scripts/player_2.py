import socket
import time
import keyboard

# NOTE: This one uses Port 8002!
UDP_IP = "127.0.0.1"
UDP_PORT = 8002

print(f"Connecting to Player 2 on {UDP_IP}:{UDP_PORT}...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("--- Player 2: Arrow Key Controller ---")
print("Controls:")
print(" UP / DOWN    : Throttle / Reverse")
print(" LEFT / RIGHT : Steer")
print(" RIGHT SHIFT  : Handbrake")
print(" ESC          : Quit")
print("--------------------------------------")

while True:
    if keyboard.is_pressed('esc'):
        print("Closing Player 2 controller.")
        break
        
    steer = 0.0
    throttle = 0.0
    handbrake = 0

    # Read Arrow Keys
    if keyboard.is_pressed('up'): throttle = 1.0
    if keyboard.is_pressed('down'): throttle = -1.0
    
    if keyboard.is_pressed('left'): steer = -1.0
    if keyboard.is_pressed('right'): steer = 1.0
    
    if keyboard.is_pressed('right shift'): handbrake = 1

    sock.sendto(f"STEER:{steer}".encode('utf-8'), (UDP_IP, UDP_PORT))
    sock.sendto(f"THROTTLE:{throttle}".encode('utf-8'), (UDP_IP, UDP_PORT))
    sock.sendto(f"HANDBRAKE:{handbrake}".encode('utf-8'), (UDP_IP, UDP_PORT))

    time.sleep(0.016)