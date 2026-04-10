import socket
import json 

def load_config(file_path="config.json"):
    with open(file_path, "r") as f:
        return json.load(f)

def send_word(sock, word):
    sock.sendall(word.encode('utf-8'))

def receive_word(sock):
    data = sock.recv(1024)
    return data.decode('utf-8')

def main():

    with open("config.json", "r") as f:
        config = json.load(f)
    host = config.get("host")
    port = config.get("port")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port)) 

        word = "start"

        while True:
            word = input("Enter word: ")

            send_word(s, word)             
            # response = receive_word(s)     
            # print("Server ACK:", response)


if __name__ == "__main__":
    main()

# Author: Wojciech "Mezyon" Jankowski