import socket
import threading
import queue
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from connection_settings import load_config

# =========================
# Konfiguracja Audio & Socket
# =========================
samplerate = 16000
block_duration = 0.5
chunk_duration = 0.75
channels = 1

frames_per_block = int(samplerate * block_duration)
frames_per_chunk = int(samplerate * chunk_duration)

audio_queue = queue.Queue()

# Lista słów, które wyzwalają wysyłkę do serwera:
KEYWORDS = ['banana', 'bomb', 'chair', 'coffee']

# =========================
# Funkcje Sieciowe
# =========================
def send_word(sock, word):
    """Wysłanie słowa przez socket"""
    try:
        sock.sendall(word.encode('utf-8'))
    except Exception as e:
        print(f"[KD] Błąd wysyłania: {e}")

# =========================
# Przetwarzanie Audio
# =========================
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

def recorder():
    """Wątek odpowiedzialny za przechwytywanie dźwięku"""
    with sd.InputStream(samplerate=samplerate, channels=channels, callback=audio_callback, blocksize=frames_per_block):
        while True:
            sd.sleep(1000)

def transcriber(sock):
    """Analizuje audio i wysyła wykryte słowa kluczowe"""
    model_size = "tiny.en"
    print(f"[KD] Ładowanie modelu {model_size}...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=8)
    audio_buffer = []

    print(f"[KD] System gotowy. Słucham słów kluczowych... ---")
    
    while True:
        block = audio_queue.get()
        audio_buffer.append(block)

        total_frames = sum(len(b) for b in audio_buffer)
        if total_frames >= frames_per_chunk:
            audio_data = np.concatenate(audio_buffer).flatten().astype(np.float32)
            audio_buffer = []

            # Transkrypcja:
            segments, _ = model.transcribe(audio_data, language="en", beam_size=1, vad_filter=True)

            for segment in segments:
                detected_text = segment.text.lower().strip().replace(".", "").replace(",", "")
                print(f"[KD] Usłyszano: {detected_text}")

                # Sprawdzanie, czy któreś ze słów kluczowych znajduje się w rozpoznanym tekście:
                for keyword in KEYWORDS:
                    if keyword in detected_text:
                        print(f"[KD] Wysłano na server: {detected_text}")
                        send_word(sock, keyword)

def main():
    config = load_config()
    host = config.get("host", "127.0.0.1")
    port = config.get("port", 65432)

    # 1. Nawiązanie połączenia i uruchomienie pętli:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            print(f"[KD] Połączono z serwerem {host}:{port}")

            # Uruchomienie nagrywania w tle:
            threading.Thread(target=recorder, daemon=True).start()

            # Uruchomienie transkrypcji (socket jako argument):
            transcriber(s)

    except ConnectionRefusedError:
        print(f"[KD] Nie udało się połączyć z serwerem. Upewnij się, że serwer działa.")
    except KeyboardInterrupt:
        print(f"[KD] Zamykanie programu...")

if __name__ == "__main__":
    main()

# Author: Wojciech "Mezyon" Jankowski