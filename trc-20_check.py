#!/usr/bin/env python3
import os
import logging
import requests
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env (если он существует)
load_dotenv()

# Параметры запроса из переменных окружения
TARGET_ADDRESS = os.getenv("TARGET_ADDRESS")
TRC20_ID = os.getenv("TRC20_ID")
START = os.getenv("START", "0")
LIMIT = os.getenv("LIMIT", "20")
DIRECTION = os.getenv("DIRECTION", "1")  # 0 – оба направления; 1 – входящие; 2 – исходящие
REVERSE = os.getenv("REVERSE", "true")
DB_VERSION = os.getenv("DB_VERSION", "1")
START_TIMESTAMP = os.getenv("START_TIMESTAMP", "")
END_TIMESTAMP = os.getenv("END_TIMESTAMP", "")

# Если заданы API-ключи (через запятую), выбираем первый
API_KEYS = os.getenv("API_KEYS", "")
api_keys = [key.strip() for key in API_KEYS.split(",")] if API_KEYS else []
API_KEY = api_keys[0] if api_keys else None

# Базовый URL для нового метода Tronscan
BASE_URL = "https://apilist.tronscanapi.com/api/transfer/trc20"

# Формирование параметров запроса
params = {
    "address": TARGET_ADDRESS,
    "trc20Id": TRC20_ID,
    "start": START,
    "limit": LIMIT,
    "direction": DIRECTION,
    "reverse": REVERSE,
    "db_version": DB_VERSION,
    "start_timestamp": START_TIMESTAMP,
    "end_timestamp": END_TIMESTAMP,
}

# Если API-ключ задан, добавляем его в параметры
if API_KEY:
    params["apikey"] = API_KEY

headers = {"accept": "application/json"}

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def main():
    logging.info("Получение списка переводов TRC20 токена для адреса %s", TARGET_ADDRESS)
    try:
        response = requests.get(BASE_URL, params=params, headers=headers)
        logging.debug("Запрос: %s", response.url)
        if response.status_code == 200:
            data = response.json()
            # Например, список переводов может быть в data['data'] (зависит от реализации API)
            transfers = data.get("data", [])
            logging.info("Запрос успешно выполнен. Получено записей: %d", len(transfers))
            print(data)
        else:
            logging.error("Ошибка %s: %s", response.status_code, response.text)
    except Exception as e:
        logging.exception("Исключение при выполнении запроса")

if __name__ == "__main__":
    main()