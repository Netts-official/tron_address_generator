#!/usr/bin/env python3
import os
import time
import threading
import multiprocessing
import logging
from tronpy.keys import PrivateKey
from pattern_matcher import PatternMatcher
import json
from datetime import datetime

# Определяем базовую директорию (на уровень выше, так как этот файл в app/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Настройка логирования для всего скрипта (общий лог)
LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, "address_generator_v2.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Глобальное событие для остановки всех потоков
stop_event = threading.Event()
# Lock для синхронизации записи красивых адресов
beautiful_lock = threading.Lock()
# Счетчики
total_generated = multiprocessing.Value('i', 0)
beautiful_found = multiprocessing.Value('i', 0)

class AddressGeneratorV2:
    def __init__(self, pattern_matcher: PatternMatcher, min_score: int = 50):
        self.matcher = pattern_matcher
        self.min_score = min_score
        self.beautiful_addresses_file = os.path.join(BASE_DIR, "addresses", "beautiful_live.txt")
        self.beautiful_json_file = os.path.join(BASE_DIR, "addresses", "beautiful_live.json")
        
        # Создаем директорию addresses если её нет
        os.makedirs(os.path.join(BASE_DIR, "addresses"), exist_ok=True)
        
        # Инициализируем файлы
        if not os.path.exists(self.beautiful_json_file):
            with open(self.beautiful_json_file, 'w') as f:
                json.dump([], f)
    
    def save_beautiful_address(self, address: str, private_key: str, analysis: dict):
        """Сохраняет красивый адрес в отдельный файл"""
        with beautiful_lock:
            # Сохраняем в текстовый файл
            with open(self.beautiful_addresses_file, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"Найден: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Адрес: {address}\n")
                f.write(f"Приватный ключ: {private_key}\n")
                f.write(f"Оценка: {analysis['score']}\n")
                f.write("Паттерны:\n")
                for pattern in analysis['patterns_found']:
                    f.write(f"  - {pattern['type']}: {pattern['pattern']} (score: {pattern['score']})\n")
                f.flush()
            
            # Добавляем в JSON файл
            try:
                with open(self.beautiful_json_file, 'r') as f:
                    beautiful_list = json.load(f)
            except:
                beautiful_list = []
            
            beautiful_list.append({
                "found_at": datetime.now().isoformat(),
                "address": address,
                "private_key": private_key,
                "score": analysis['score'],
                "patterns": analysis['patterns_found']
            })
            
            with open(self.beautiful_json_file, 'w') as f:
                json.dump(beautiful_list, f, indent=2)
            
            beautiful_found.value += 1
            
            # Выводим в консоль
            print(f"\n🎉 НАЙДЕН КРАСИВЫЙ АДРЕС! (Score: {analysis['score']})")
            print(f"   Адрес: {address}")
            patterns_str = ", ".join([f"{p['type']}:{p['pattern']}" for p in analysis['patterns_found']])
            print(f"   Паттерны: {patterns_str}")
            print(f"   Всего найдено красивых: {beautiful_found.value}\n")
    
    def worker(self, thread_id: int, save_all: bool = True):
        """
        Функция-воркер для потока с проверкой на красивые адреса
        """
        thread_filename = os.path.join(BASE_DIR, "addresses", f"addresses_thread_{thread_id}.txt")
        logging.info(f"Поток {thread_id}: запуск (save_all={save_all})")
        
        try:
            # Открываем файл только если save_all=True
            file_handle = open(thread_filename, "a") if save_all else None
            
            iteration = 0
            local_beautiful = 0
            
            while not stop_event.is_set():
                iteration += 1
                
                # Генерируем адрес
                priv_key = PrivateKey.random()
                address = priv_key.public_key.to_base58check_address()
                
                # Увеличиваем счетчик
                with total_generated.get_lock():
                    total_generated.value += 1
                
                # Анализируем адрес
                analysis = self.matcher.analyze_address(address)
                
                # Если адрес красивый
                if analysis["score"] >= self.min_score:
                    local_beautiful += 1
                    self.save_beautiful_address(address, priv_key.hex(), analysis)
                
                # Сохраняем все адреса если save_all=True
                if save_all and file_handle:
                    line = f"Address: {address}, PrivateKey: {priv_key.hex()}, Score: {analysis['score']}\n"
                    file_handle.write(line)
                    file_handle.flush()
                
                # Показываем прогресс каждые 10000 итераций
                if iteration % 10000 == 0:
                    logging.info(f"Поток {thread_id}: {iteration} адресов, {local_beautiful} красивых найдено")
                
                # Небольшая задержка для снижения нагрузки
                if iteration % 100 == 0:
                    time.sleep(0.001)
                    
        except Exception as e:
            logging.exception(f"Поток {thread_id}: ошибка при генерации адресов")
        finally:
            if file_handle:
                file_handle.close()
        
        logging.info(f"Поток {thread_id} завершён. Найдено красивых: {local_beautiful}")


def print_statistics():
    """Выводит статистику генерации каждые 5 секунд"""
    start_time = time.time()
    last_total = 0
    
    while not stop_event.is_set():
        time.sleep(5)
        current_total = total_generated.value
        current_beautiful = beautiful_found.value
        elapsed_time = time.time() - start_time
        
        # Скорость генерации
        addresses_per_second = (current_total - last_total) / 5
        total_speed = current_total / elapsed_time if elapsed_time > 0 else 0
        
        # Статистика
        print(f"\n📊 СТАТИСТИКА:")
        print(f"   Время работы: {int(elapsed_time)}с")
        print(f"   Всего сгенерировано: {current_total:,}")
        print(f"   Красивых найдено: {current_beautiful}")
        print(f"   Скорость: {addresses_per_second:.0f} адр/сек (средняя: {total_speed:.0f} адр/сек)")
        if current_beautiful > 0:
            print(f"   Частота красивых: 1 из {current_total // current_beautiful:,}")
        
        last_total = current_total


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Генератор красивых TRON адресов v2')
    parser.add_argument('--threads', '-t', type=int, default=10,
                       help='Количество потоков (по умолчанию: 10)')
    parser.add_argument('--min-score', '-s', type=int, default=50,
                       help='Минимальная оценка для красивого адреса (по умолчанию: 50)')
    parser.add_argument('--no-save-all', action='store_true',
                       help='Не сохранять все адреса, только красивые')
    parser.add_argument('--patterns-file', '-p',
                       help='Файл с настройками паттернов (JSON)')
    
    args = parser.parse_args()
    
    # Создаем matcher
    matcher = PatternMatcher(args.patterns_file)
    generator = AddressGeneratorV2(matcher, args.min_score)
    
    logging.info(f"Запуск генератора TRON адресов v2")
    logging.info(f"Потоков: {args.threads}")
    logging.info(f"Минимальная оценка: {args.min_score}")
    logging.info(f"Сохранять все адреса: {not args.no_save_all}")
    
    print(f"\n🚀 ГЕНЕРАТОР КРАСИВЫХ TRON АДРЕСОВ V2")
    print(f"{'='*50}")
    print(f"Потоков: {args.threads}")
    print(f"Минимальная оценка для красивого адреса: {args.min_score}")
    print(f"Сохранение всех адресов: {'Да' if not args.no_save_all else 'Нет'}")
    print(f"Красивые адреса сохраняются в: addresses/beautiful_live.txt")
    print(f"{'='*50}")
    print(f"Нажмите Ctrl+C для остановки\n")
    
    # Запускаем поток статистики
    stats_thread = threading.Thread(target=print_statistics, daemon=True)
    stats_thread.start()
    
    # Запускаем рабочие потоки
    threads = []
    try:
        for i in range(1, args.threads + 1):
            t = threading.Thread(
                target=generator.worker, 
                args=(i, not args.no_save_all)
            )
            t.start()
            threads.append(t)
        
        # Ожидаем нажатия Ctrl+C
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⏸️  Остановка генератора...")
        stop_event.set()
    
    # Ожидаем завершения всех потоков
    for t in threads:
        t.join()
    
    print(f"\n✅ Генерация завершена")
    print(f"   Всего сгенерировано: {total_generated.value:,}")
    print(f"   Красивых найдено: {beautiful_found.value}")
    print(f"   Результаты сохранены в: addresses/beautiful_live.txt")


if __name__ == "__main__":
    main()