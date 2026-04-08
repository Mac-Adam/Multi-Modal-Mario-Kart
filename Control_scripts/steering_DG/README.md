## 1. Opis Projektu

System służy do bezdotykowego sterowania pojazdem w środowisku Unreal Engine za pomocą kamery RGB.  
System analizuje pozycję lub orientację markerów (wydruków 3D) przymocowanych do dłoni użytkownika i przesyła znormalizowaną wartość skrętu przez protokół UDP.

## 2. Wymagania Techniczne

- **Python:** 3.8 - 3.12
- **Biblioteki:** opencv-python, numpy  
- **Sprzęt:**  
  - Kamera internetowa (zalecane 30/60 FPS)  
  - Markery w kolorze błękitnym/niebieskim (matowe)

## 3. Specyfikacja Protokołu UDP (Dla Zespołu Unreal Engine)

| Parametr          | Wartość                         |
|-------------------|--------------------------------|
| Protokół          | UDP (Bezpołączeniowy)           |
| Adres IP          | 127.0.0.1 (localhost)           |
| Port              | 8001                           |
| Format Wiadomości  | Ciąg znaków (String) w formacie: `STEER:value` |
| Zakres value      | od -1.000 (Max Lewo) do 1.000 (Max Prawo) |
| Częstotliwość     | Obecnie zależna od czasu obliczeń pojedynczej pętli   |

**Przykład odebranego pakietu:**  
`STEER:0.453`

## 4. Metody Analizy Obrazu

System wspiera dwa alternatywne podejścia do wyliczania wartości skrętu.

### Metoda A: Orientacja Kątowa Strzałek `steering_w_angles`

- Analizuje kąt nachylenia każdej strzałki z osobna względem pionu.  
- Działanie: Wykorzystuje algorytm `cv2.fitLine` do wyznaczenia osi podłużnej markera.  
- Zaleta: Umożliwia sterowanie jedną ręką; bardzo precyzyjne przy obrotach nadgarstka.  
- Zakres pracy: Pełny skręt (1.0) osiągany przy pochyleniu o 80° od pionu.

### Metoda B: Centroidy (Kąt Między Dłońmi) `steering_w_centroids`

- Analizuje kąt linii łączącej środki ciężkości obu markerów.  
- Działanie: Wyznacza punkty środkowe (momenty) dwóch największych obiektów i liczy nachylenie wirtualnej osi między nimi.  
- Zaleta: Bardzo stabilne, imituje trzymanie fizycznej kierownicy.  
- Zakres pracy: Pełny skręt (1.0) osiągany przy nachyleniu linii dłoni o 80°.

## 5. Przetwarzanie i Filtrowanie

W celu eliminacji szumów i drgań kamery, w skrypcie `main_controller.py` zastosowano filtr dolnoprzepustowy (Exponential Moving Average):

```python
smoothed_steer = (alpha * steer_val) + ((1 - alpha) * smoothed_steer)
```
- **Alpha (0.2):** Parametr ten można modyfikować.  
- Niższa wartość = większa płynność, ale większe opóźnienie.

## 6. Struktura Plików

- `steering_logic.py`: Moduł obliczeniowy. Zawiera preprocessing obrazu (przestrzeń CIELAB), detekcję konturów oraz algorytmy geometryczne.  
- `main_controller.py`: Skrypt uruchomieniowy. Obsługuje przechwytywanie wideo, wygładzanie danych, wysyłkę UDP oraz podgląd (UI).

## 7. Instrukcja Kalibracji (Dla Operatora)

- Ustaw oświetlenie tak, aby markery były najjaśniejszymi elementami koloru błękitnego w kadrze.  
- W pliku `main_controller.py` dostosuj tablice `LOWER_COLOR` i `UPPER_COLOR` w przestrzeni CIELAB, jeśli system nie odcina tła poprawnie.  
- Uruchom skrypt i obserwuj okno Mask. Powinno zawierać tylko dwa wyraźne, białe kształty na czarnym tle.