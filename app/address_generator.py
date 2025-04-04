#!/usr/bin/env python3
import os
import time
import threading
import logging
from tronpy.keys import PrivateKey

# Определяем базовую директорию (на уровень выше, так как этот файл в app/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Настройка логирования для всего скрипта (общий лог)
LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, "address_generator.log")
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Глобальное событие для остановки всех потоков, когда найден нужный адрес
found_event = threading.Event()

def worker(thread_id):
    """
    Функция-воркер для потока. В бесконечном цикле генерирует адреса,
    записывает их в файл и проверяет, соответствует ли сгенерированный адрес требуемому шаблону.
    """
    thread_filename = os.path.join(BASE_DIR, f"addresses_thread_{thread_id}.txt")
    logging.info(f"Поток {thread_id}: запись в файл {thread_filename}")
    
    try:
        with open(thread_filename, "a") as f:
            iteration = 0
            while not found_event.is_set():
                iteration += 1
                priv_key = PrivateKey.random()
                address = priv_key.public_key.to_base58check_address()
                line = f"Address: {address}, PrivateKey: {priv_key.hex()}\n"
                f.write(line)
                f.flush()  # чтобы данные сразу записывались в файл
                logging.debug(f"Поток {thread_id}, Итерация {iteration}: сгенерирован адрес {address}")
                
                # Проверяем, оканчивается ли адрес на "Netts" или "Nettsio"
                if address.endswith("Netts") or address.endswith("Nettsio"):
                    logging.info(f"Поток {thread_id} нашёл подходящий адрес: {address}")
                    found_event.set()
                    break
                # Небольшая задержка (можно уменьшить/увеличить при необходимости)
                time.sleep(0.01)
    except Exception as e:
        logging.exception(f"Поток {thread_id}: ошибка при генерации адресов")
    logging.info(f"Поток {thread_id} завершён.")

def main():
    logging.info("Запуск генератора TRON адресов в 10 потоках...")
    threads = []
    num_threads = 50
    for i in range(1, num_threads + 1):
        t = threading.Thread(target=worker, args=(i,))
        t.start()
        threads.append(t)
    
    # Ожидаем завершения всех потоков
    for t in threads:
        t.join()
    
    logging.info("Генерация завершена. Подходящий адрес найден.")

if __name__ == "__main__":
    main()