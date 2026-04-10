import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel

def main():
    # =========================
    # Konfiguracja nagrywania
    # =========================
    fs = 16000              # Częstotliwość próbkowania
    seconds = 5             # Długość nagrania
    filename = "voice.wav"  # Nazwa pliku z tekstem do transkrypcji

    print(f"Nagrywanie przez {seconds} sekund...")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  
    print("Nagrywanie zakończone.")

    # Zapis do pliku tymczasowego:
    wav.write(filename, fs, myrecording)

    # =========================
    # Inicjalizacja modelu
    # =========================
    model_size = "tiny.en"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    # =========================
    # Transkrypcja
    # =========================
    print("Rozpoczynam transkrypcję...")
    segments, info = model.transcribe(filename, beam_size=5)

    print("-" * 30)
    print(f"Wykryty język: {info.language} (prawdopodobieństwo: {info.language_probability:.2f})")

    for segment in segments:
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")

if __name__ == "__main__":
    main()

# Author: Wojciech "Mezyon" Jankowski