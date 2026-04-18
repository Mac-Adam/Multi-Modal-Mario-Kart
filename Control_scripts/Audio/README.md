# Real-Time Keyword Detection System

Profesjonalne narzędzie do analizy strumienia audio w czasie rzeczywistym, wykorzystujące model **Whisper** do detekcji słów kluczowych i komunikację poprzez protokół **TCP/IP (Sockets)**.

---

## 📝 Opis projektu
System umożliwia ciągłe monitorowanie sygnału z mikrofonu, automatyczną transkrypcję mowy na tekst oraz natychmiastowe przesyłanie zidentyfikowanych słów kluczowych do zewnętrznego serwera. Rozwiązanie zostało zoptymalizowane pod kątem niskich opóźnień i minimalnego obciążenia zasobów sprzętowych.

## 🚀 Kluczowe funkcje
* **Analiza Live:** Przetwarzanie potokowe audio bezpośrednio z urządzenia wejściowego.
* **Wydajność:** Wykorzystanie silnika `faster-whisper` z kwantyzacją `int8` dla optymalizacji pracy na procesorach (CPU).
* **Elastyczność:** Możliwość łatwej rekonfiguracji parametrów sieciowych oraz listy słów kluczowych.
* **Komunikacja Sieciowa:** Integracja z serwerami zewnętrznymi za pomocą gniazd (sockets).

## 🧩 Wymagania systemowe
* **Python:** wersja 3.8 lub nowsza.
* **Biblioteki:** pobranie bibliotek z pliku: requirements.txt
* **Sprzęt:** Sprawne urządzenie przechwytujące dźwięk (mikrofon).

## ⚙️ Konfiguracja

### 1. Plik konfiguracyjny
System ładuje parametry sieciowe z pliku `config.json`. Należy upewnić się, co do zgodności konfiguracji z serverem:

```json
{
  "host": "127.0.0.1",
  "port": 65432
}
```

### 2. Definicja słów kluczowych
Słowa kluczowe są obecnie definiowane bezpośrednio w kodzie źródłowym w liście KEYWORDS:

```
KEYWORDS = ['banana', 'bomb', 'chair', 'coffee']
```

##  ▶️ Uruchomienie
Aby zainicjować proces detekcji, należy wykonać skrypt:

```
python keyword_detection.py
```

## 🧠 Architektura rozwiązania
* **Ingestia:** Przechwytywanie próbek audio do bufora kołowego.
* **Segmentacja:** Dzielenie strumienia na interwały czasowe (domyślnie ok. 0.75s).
* **Inferencja:** Proces transkrypcji realizowany przez model WhisperModel.
* **Ekstrakcja:** Porównywanie wyników tekstowych ze zdefiniowanym słownikiem.
* **Transmisja:** Wysyłanie pakietu danych do serwera TCP po wykryciu dopasowania.

## ⚠️ Specyfikacja techniczna i optymalizacja
* **Model:** Domyślnie wykorzystywany jest model tiny.en (zoptymalizowany pod język angielski).
* **Zasoby:** Inicjalizacja modelu odbywa się domyślnie z parametrem device="cpu" na 8 rdzeniach procesora. Ustawinia te można zmieńć w zależnosci od sprzętu. W przypadku posiadania układu graficznego NVIDIA, można zmienić parametr device na cuda w celu zwiększenia wydajności.
* **Latencja:** Czas reakcji systemu jest bezpośrednio uzależniony od parametru chunk_duration oraz mocy obliczeniowej jednostki CPU/GPU.

## 📄 Autor
Wojciech "Mezyon" Jankowski