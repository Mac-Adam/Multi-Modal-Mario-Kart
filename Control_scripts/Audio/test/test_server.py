import socket
import json 

def send_word(conn, word):
    conn.sendall(word.encode('utf-8'))

def receive_word(conn):
    data = conn.recv(1024)
    if not data:
        return None
    return data.decode('utf-8')

def main():

    with open("config.json", "r") as f:
        config = json.load(f)
        
    host = config.get("host")
    port = config.get("port")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        print("Server is listening...")
        conn, addr = s.accept()

        with conn:
            print(f"Connected by {addr}")

            while True:
                word = receive_word(conn)
                if word is None:
                    break

                print("Word:", word)

                send_word(conn, f"{word}")


if __name__ == "__main__":
    main()

# Author: Wojciech "Mezyon" Jankowski