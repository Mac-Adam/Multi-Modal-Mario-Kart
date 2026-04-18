import json
from pathlib import Path


def load_config(file_path="connection_settings.json"):
    config_path = Path(file_path)
    if not config_path.is_absolute():
        config_path = (Path(__file__).resolve().parent / config_path).resolve()

    try:
        with open(config_path, "r", encoding="utf-8") as file_handle:
            config = json.load(file_handle)
            print(
                f"[CFG] Załadowano konfigurację z {config_path} "
                f"(host={config.get('host', '127.0.0.1')}, port={config.get('port', 65432)})"
            )
            return config
    except FileNotFoundError:
        print(
            f"[CFG] Nie znaleziono pliku konfiguracyjnego {config_path}. "
            "Używam domyślnych ustawień."
        )
        return {"host": "127.0.0.1", "port": 65432}
    except json.JSONDecodeError as error:
        print(
            f"[CFG] Nieprawidłowy JSON w {config_path}: {error}. "
            "Używam domyślnych ustawień."
        )
        return {"host": "127.0.0.1", "port": 65432}
