# Moduł Sterowania Kamerą

Ten folder zawiera plik `camera_module.py`, czyli moduł sterowania oparty na wizji komputerowej dla Unreal Engine.

## Co robi ten skrypt

- Przechwytuje obraz z kamery internetowej przez OpenCV.
- Wykrywa dwie dłonie przy użyciu MediaPipe Hands.
- Oblicza wartość skrętu na podstawie kąta między pozycjami dłoni.
- Wygładza skręt filtrem dolnoprzepustowym.
- Wysyła pakiety sterowania po UDP w formacie `STEER:<wartość>`.
- Wyświetla podgląd na żywo z FPS i aktualną wartością skrętu.

## Konfiguracja sieci

Skrypt ładuje ustawienia połączenia z pliku `connection_settings.json` (z poziomu katalogu głównego projektu) przez funkcję `load_config()` w `connection_settings.py`.

## Uruchomienie

Z katalogu głównego projektu:

```bash
python Control_scripts/Camera/camera_module.py
```

