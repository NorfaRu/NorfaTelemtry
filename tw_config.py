import json
import os

DEFAULT_CONFIG = {
    "packet_structure": {
        "format": "<2HIhI6hBHBH4h3fB3HB",  # Формат структуры пакета
        "fields": [
            {"name": "header", "type": "bytes", "length": 2, "description": "Заголовок пакета (0xAA 0xAA)"},
            {"name": "packet_num", "type": "int", "index": 12, "description": "Номер пакета"},
            {"name": "timestamp", "type": "int", "index": 2, "description": "Время"},
            {"name": "temp_bmp", "type": "float", "index": 3, "scale": 0.01, "description": "Температура BMP"},
            {"name": "press_bmp", "type": "int", "index": 4, "description": "Давление BMP"},
            {"name": "accel", "type": "vector3", "indices": [5, 6, 7], "scale": 0.000488, "description": "Акселерометр"},
            {"name": "gyro", "type": "vector3", "indices": [8, 9, 10], "scale": 0.07, "description": "Гироскоп"},
            {"name": "state", "type": "int", "index": 13, "mask": 7, "description": "Состояние"},
            {"name": "photo", "type": "float", "index": 14, "scale": 0.001, "description": "Фото"},
            {"name": "mag", "type": "vector3", "indices": [15, 16, 17], "scale": 1/1711, "description": "Магнитометр"},
            {"name": "temp_ds", "type": "float", "index": 18, "scale": 1/16, "description": "Температура DS"},
            {"name": "gps", "type": "vector3", "indices": [19, 20, 21], "description": "GPS"},
            {"name": "gps_fix", "type": "int", "index": 22, "description": "GPS Fix"},
            {"name": "scd41", "type": "int", "index": 23, "description": "SCD41"},
            {"name": "mq4", "type": "int", "index": 24, "description": "MQ4"},
            {"name": "me2o2", "type": "int", "index": 25, "description": "ME2O2"},
            {"name": "crc", "type": "int", "index": -1, "description": "Контрольная сумма1"}
        ]
    },
    "telemetry_view": {
        "fields": [
            {"label": "Номер пакета",   "source": "packet_num", "format": "{}"},
            {"label": "Время, мс",      "source": "timestamp",  "format": "{}"},
            {"label": "Темп BMP, °C",   "source": "temp_bmp",   "format": "{:.2f}"},
            {"label": "Давл BMP, Па",   "source": "press_bmp",  "format": "{}"},
            {"label": "Ускор (X Y Z)",  "source": "accel",      "format": "[{:.2f}, {:.2f}, {:.2f}]"},
            {"label": "Угл.скор (X Y Z)","source": "gyro",       "format": "[{:.2f}, {:.2f}, {:.2f}]"},
            {"label": "Сост. аппарата", "source": "state",      "format": "{}"},
            {"label": "Фото.рез, В",    "source": "photo",      "format": "{:.3f}"},
            # Increased precision for magnetometer display as values might be small
            {"label": "Магн. поле (X Y Z)","source":"mag",        "format": "[{:.4f}, {:.4f}, {:.4f}]"},
            {"label": "Темп DS18, °C",  "source": "temp_ds",    "format": "{:.2f}"},
            {"label": "GPS (lat lon h)", "source": "gps",        "format": "[{:.6f}, {:.6f}, {:.2f}]"},
            {"label": "GPS fix",        "source": "gps_fix",    "format": "{}"},
            {"label": "SCD41",          "source": "scd41",      "format": "{}"},
            {"label": "MQ-4, ppm",      "source": "mq4",        "format": "{}"},
            {"label": "ME2-O2, ppm",    "source": "me2o2",      "format": "{}"},
            {"label": "Контр. сумма",   "source": "crc",        "format": "{}"}
        ]
    },
    "graphs": [
        {"name": "temp_bmp",  "title": "Темп BMP",      "type": "line", "source": "temp_bmp",   "color": "#e57373", "y_min": -40,   "y_max": 85,     "position": [0,0], "size": [1,1]},
        {"name": "press_bmp", "title": "Давл BMP",      "type": "line", "source": "press_bmp",  "color": "#4fc3f7", "y_min": 30000, "y_max": 110000, "position": [0,1], "size": [1,1]},
        {"name": "accel_x",   "title": "Accel X",      "type": "line", "source": "accel[0]",   "color": "#81c784", "y_min": -10,   "y_max": 10,     "position": [1,0], "size": [1,1]},
        {"name": "accel_y",   "title": "Accel Y",      "type": "line", "source": "accel[1]",   "color": "#ffb74d", "y_min": -10,   "y_max": 10,     "position": [1,1], "size": [1,1]},
        {"name": "accel_z",   "title": "Accel Z",      "type": "line", "source": "accel[2]",   "color": "#64b5f6", "y_min": -10,   "y_max": 10,     "position": [2,0], "size": [1,1]},
        {"name": "gyro_x",    "title": "Gyro X",       "type": "line", "source": "gyro[0]",    "color": "#ba68c8", "y_min": -250,  "y_max": 250,    "position": [2,1], "size": [1,1]},
        {"name": "gyro_y",    "title": "Gyro Y",       "type": "line", "source": "gyro[1]",    "color": "#ff8a65", "y_min": -250,  "y_max": 250,    "position": [3,0], "size": [1,1]},
        {"name": "gyro_z",    "title": "Gyro Z",       "type": "line", "source": "gyro[2]",    "color": "#ffd54f", "y_min": -250,  "y_max": 250,    "position": [3,1], "size": [1,1]},
        {"name": "mag_x",     "title": "Mag X",        "type": "line", "source": "mag[0]",     "color": "#4db6ac", "y_min": -1000, "y_max": 1000,   "position": [4,0], "size": [1,1]},
        {"name": "mag_y",     "title": "Mag Y",        "type": "line", "source": "mag[1]",     "color": "#90caf9", "y_min": -1000, "y_max": 1000,   "position": [4,1], "size": [1,1]},
        {"name": "mag_z",     "title": "Mag Z",        "type": "line", "source": "mag[2]",     "color": "#a1887f", "y_min": -1000, "y_max": 1000,   "position": [5,0], "size": [1,1]},
        {"name": "temp_ds",   "title": "Темп DS",      "type": "line", "source": "temp_ds",    "color": "#4e342e", "y_min": -40,   "y_max": 85,     "position": [5,1], "size": [1,1]},
        {"name": "photo",     "title": "Фото",         "type": "line", "source": "photo",      "color": "#90a4ae", "y_min":   0,   "y_max": 1,      "position": [6,0], "size": [1,1]},
        {"name": "scd41",     "title": "SCD41",        "type": "line", "source": "scd41",      "color": "#c0ca33", "y_min":   0,   "y_max": 1000,   "position": [6,1], "size": [1,1]},
        {"name": "mq4",       "title": "MQ4",          "type": "line", "source": "mq4",        "color": "#f06292", "y_min":   0,   "y_max": 1000,   "position": [7,0], "size": [1,1]},
        {"name": "me2o2",     "title": "ME2O2",        "type": "line", "source": "me2o2",      "color": "#ba68c8", "y_min":   0,   "y_max": 1000,   "position": [7,1], "size": [1,1]}
    ]
}

def load_config():
    """Загрузка конфигурации из файла или создание файла с дефолтной конфигурацией"""
    path = "telemetry_config.json"
    if os.path.exists(path):
        try:
            # Ensure reading with UTF-8 encoding
            with open(path, 'r', encoding="utf-8") as f:
                config_data = json.load(f)
            # Optional: Add validation or migration logic here if needed
            return config_data
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON в файле конфигурации: {e}")
            print(f"Файл '{path}' может быть поврежден.")
            print("Попытка создать файл конфигурации по умолчанию.")
            try:
                # Create default config file
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
                print(f"Создан новый файл конфигурации '{path}' с настройками по умолчанию.")
                return DEFAULT_CONFIG
            except Exception as write_e:
                print(f"Не удалось создать файл конфигурации по умолчанию: {write_e}")
                print("Используется конфигурация по умолчанию в памяти.")
                return DEFAULT_CONFIG # Return default config from memory as fallback
        except Exception as e:
            print(f"Непредвиденная ошибка при загрузке конфигурации: {e}")
            print("Используется конфигурация по умолчанию в памяти.")
            # Optionally try to recreate the default file here too, or just use in-memory
            return DEFAULT_CONFIG # Return default config from memory as fallback
    else:
        print(f"Файл конфигурации '{path}' не найден.")
        print("Создание файла с конфигурацией по умолчанию.")
        try:
            # Create default config file
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
            print(f"Создан файл конфигурации '{path}' с настройками по умолчанию.")
            return DEFAULT_CONFIG
        except Exception as e:
            print(f"Не удалось создать файл конфигурации по умолчанию: {e}")
            print("Используется конфигурация по умолчанию в памяти.")
            return DEFAULT_CONFIG # Return default config from memory as fallback