# Examples

Krótki folder z prostymi kontrolerami klawiaturowymi wysyłającymi komendy UDP do gry.

## Pliki

- `player_1.py` - sterowanie `WASD` + `SPACE`, wysyłka UDP na podstawie `connection_settings.json`.
- `player_2.py` - sterowanie strzałkami + `RIGHT SHIFT`, wysyłka UDP na podstawie `connection_settings.json`.

## Konfiguracja sieci

Oba skrypty ładują ustawienia przez `load_config()` z `connection_settings.py`.

Używane pola:

- `udp_ip` (fallback: `host`, a potem `127.0.0.1`)
- `udp_port` (dla `player_1.py`, fallback: `8001`)
- `udp_port_player2` (dla `player_2.py`, fallback: `8002`)

## Uruchomienie

Z katalogu głównego projektu:

```bash
python Control_scripts/Examples/player_1.py
```

lub

```bash
python Control_scripts/Examples/player_2.py
```
