# Multi Modal Mario Kart

Projekt realizowany w ramach przedmiotu Interfejsy człowiek komputer na 1 roku studiów magisterskich Automatyka i 
Robotyka.

### Cel

Projekt miał na celu realizacje gry inspirowanej na Mario Kart natomiast zamieniając sterowanie na bazujące na wielomodalnościowym podejściu. Zaproponowane przez nas sterowanie opiera się na wizji, dzwięku oraz dotyku. Takie rozwiązanie może zapewnić nadzwyczajne doświadczenia z gry oraz stanowić bazę pod multimodalne interfejsy użytkownika w przyszłości, które dzięki rozwojowi metod analizy danych i sztucznej inteligencji zyskują popularność.

### Struktura

Projekt składa się z 2 kluczowych folderów

- **Unreal_project** w którym znajduje się gra stworzona z pomocą silnika Unreal Engine
- **Control_scripts** zawierający skrypty w pythonie umożliwiające wielomodalnościowe sterowanie

### Komunikacja

Komunikacja z grą odbywa się za pomocą protokołu udp i jest zdefiniowana w pliku connection_settings.json.

### Modalności

Sterowanie grą składa się z poniższych modalności

- [Wizja](Control_scripts/steering_DG)
- [Wizja 2](Control_scripts/Camera)
- [Dzwięk](Control_scripts/Audio)
- [Dotyk](Control_scripts/Pedal)
- [Klawiatura(przykład)](Control_scripts/Examples)

### Jak uruchomić wszystkie modalności

Uruchamiaj każdą modalność w osobnym terminalu (z katalogu głównego projektu). Najpierw uruchom Unreal Engine, potem skrypty sterujące.

Przykładowa kolejność:

1. Unreal Engine (`Unreal_project`).
2. Dotyk (pedal):

```bash
python Control_scripts/Pedal/Program/komunikacja/comms.py
```

3. Dzwięk:

```bash
python Control_scripts/Audio/keyword_detection.py
```

4. Wizja (wybierz jedną wersję):

```bash
python Control_scripts/steering_DG/steering_w_angles/main_controller.py
```

lub

```bash
python Control_scripts/steering_DG/steering_w_centroids/main_controller.py
```

5. Wizja 2 (MediaPipe Hands):

```bash
python Control_scripts/Camera/camera_module.py
```

6. Klawiatura (opcjonalnie, przykład):

```bash
python Control_scripts/Examples/player_1.py
```

Wszystkie skrypty korzystają z ustawień sieciowych z `connection_settings.json`.