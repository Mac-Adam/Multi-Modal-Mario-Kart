import socket
import time
import keyboard

# Match your Unreal Engine settings
UDP_IP = "127.0.0.1"
UDP_PORT = 8001

print(f"Connecting to Unreal Engine on {UDP_IP}:{UDP_PORT}...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("--- Multimodal Mario Kart: WASD Controller ---")
print("Controls:")
print(" W / S : Throttle / Reverse")
print(" A / D : Steer Left / Right")
print(" SPACE : Handbrake")
print(" ESC   : Quit")
print("----------------------------------------------")

# We run a continuous loop to stream data, just like a real game controller
while True:
    if keyboard.is_pressed('esc'):
        print("Closing controller.")
        break
        
    # Default values (if you let go of the keys, the car should stop/center)
    steer = 0.0
    throttle = 0.0
    handbrake = 0

    # Read WASD
    if keyboard.is_pressed('w'): throttle = 1.0
    if keyboard.is_pressed('s'): throttle = -1.0 # Negative throttle is reverse
    
    if keyboard.is_pressed('a'): steer = -1.0
    if keyboard.is_pressed('d'): steer = 1.0
    
    if keyboard.is_pressed('space'): handbrake = 1

    # Send the packets
    sock.sendto(f"STEER:{steer}".encode('utf-8'), (UDP_IP, UDP_PORT))
    sock.sendto(f"THROTTLE:{throttle}".encode('utf-8'), (UDP_IP, UDP_PORT))
    sock.sendto(f"HANDBRAKE:{handbrake}".encode('utf-8'), (UDP_IP, UDP_PORT))

    # Sleep for 16 milliseconds to send data at roughly 60 Frames Per Second
    # This prevents the script from overloading your network or CPU
    time.sleep(0.016)