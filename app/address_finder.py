#!/usr/bin/env python3
import os
import sys
import argparse
import json
from typing import List, Dict, Optional
from pattern_matcher import PatternMatcher
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class AddressFinder:
    """Класс для поиска красивых адресов в существующих файлах"""
    
    def __init__(self, pattern_matcher: PatternMatcher):
        self.matcher = pattern_matcher
        self.results = []
    
    def scan_file(self, filename: str, min_score: int = 50) -> List[Dict]:
        """Сканирует файл и находит красивые адреса"""
        beautiful_addresses = []
        
        if not os.path.exists(filename):
            print(f"Файл {filename} не найден")
            return beautiful_addresses
        
        print(f"Сканирование файла: {filename}")
        line_count = 0
        
        try:
            with open(filename, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line_count += 1
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Извлекаем адрес и приватный ключ
                    if "Address:" in line and "PrivateKey:" in line:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            address_part = parts[0].split(':', 1)
                            key_part = parts[1].split(':', 1)
                            
                            if len(address_part) == 2 and len(key_part) == 2:
                                address = address_part[1].strip()
                                private_key = key_part[1].strip()
                                
                                # Анализируем адрес
                                analysis = self.matcher.analyze_address(address)
                                
                                if analysis["score"] >= min_score:
                                    result = {
                                        "file": filename,
                                        "line": line_num,
                                        "address": address,
                                        "private_key": private_key,
                                        "score": analysis["score"],
                                        "patterns": analysis["patterns_found"]
                                    }
                                    beautiful_addresses.append(result)
                    
                    # Показываем прогресс каждые 10000 строк
                    if line_count % 10000 == 0:
                        print(f"  Обработано {line_count} строк, найдено {len(beautiful_addresses)} красивых адресов")
        
        except Exception as e:
            print(f"Ошибка при чтении файла {filename}: {e}")
        
        print(f"  Всего обработано {line_count} строк, найдено {len(beautiful_addresses)} красивых адресов")
        return beautiful_addresses
    
    def scan_directory(self, directory: str = None, pattern: str = "addresses*.txt", min_score: int = 50) -> List[Dict]:
        """Сканирует все файлы адресов в директории и подпапках"""
        if directory is None:
            directory = os.path.join(BASE_DIR, "addresses")
        
        all_results = []
        
        # Список директорий для поиска
        search_dirs = [
            directory,
            os.path.join(directory, "old"),
            os.path.join(directory, "old_1")
        ]
        
        # Ищем файлы во всех директориях
        all_files = []
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                # Ищем в текущей директории
                files = glob.glob(os.path.join(search_dir, pattern))
                all_files.extend(files)
                
                # Также ищем рекурсивно во всех подпапках
                recursive_pattern = os.path.join(search_dir, "**", pattern)
                recursive_files = glob.glob(recursive_pattern, recursive=True)
                all_files.extend(recursive_files)
        
        # Убираем дубликаты
        all_files = list(set(all_files))
        
        if not all_files:
            print(f"Файлы по паттерну {pattern} не найдены")
            return all_results
        
        print(f"Найдено файлов для сканирования: {len(all_files)}")
        print(f"Директории поиска: {', '.join(search_dirs)}")
        
        for file_path in sorted(all_files):
            results = self.scan_file(file_path, min_score)
            all_results.extend(results)
        
        return all_results
    
    def filter_by_pattern_type(self, results: List[Dict], pattern_type: str) -> List[Dict]:
        """Фильтрует результаты по типу паттерна"""
        filtered = []
        for result in results:
            for pattern in result["patterns"]:
                if pattern["type"] == pattern_type:
                    filtered.append(result)
                    break
        return filtered
    
    def filter_by_word(self, results: List[Dict], word: str) -> List[Dict]:
        """Фильтрует результаты по наличию слова"""
        filtered = []
        word_upper = word.upper()
        for result in results:
            if word_upper in result["address"].upper():
                filtered.append(result)
        return filtered
    
    def save_results(self, results: List[Dict], output_file: str):
        """Сохраняет результаты в файл"""
        output_path = os.path.join(BASE_DIR, "addresses", output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Сохраняем в JSON формате для программной обработки
        json_file = output_path.replace('.txt', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Сохраняем в читаемом текстовом формате
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Найдено красивых адресов: {len(results)}\n")
            f.write("=" * 80 + "\n\n")
            
            # Сортируем по score
            sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
            
            for i, result in enumerate(sorted_results, 1):
                f.write(f"#{i} Адрес: {result['address']}\n")
                f.write(f"Приватный ключ: {result['private_key']}\n")
                f.write(f"Оценка: {result['score']}\n")
                f.write(f"Файл: {result['file']}, строка: {result['line']}\n")
                f.write("Найденные паттерны:\n")
                for pattern in result["patterns"]:
                    f.write(f"  - {pattern['type']}: {pattern['pattern']} (score: {pattern['score']})\n")
                f.write("-" * 80 + "\n\n")
        
        print(f"\nРезультаты сохранены в:")
        print(f"  - {output_path} (текстовый формат)")
        print(f"  - {json_file} (JSON формат)")
    
    def print_summary(self, results: List[Dict]):
        """Выводит сводку найденных адресов"""
        if not results:
            print("\nКрасивых адресов не найдено")
            return
        
        print(f"\n{'='*80}")
        print(f"СВОДКА: Найдено {len(results)} красивых адресов")
        print(f"{'='*80}\n")
        
        # Статистика по типам паттернов
        pattern_stats = {}
        for result in results:
            for pattern in result["patterns"]:
                ptype = pattern["type"]
                if ptype not in pattern_stats:
                    pattern_stats[ptype] = 0
                pattern_stats[ptype] += 1
        
        print("Статистика по типам паттернов:")
        for ptype, count in sorted(pattern_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {ptype}: {count} адресов")
        
        # Топ-10 адресов по score
        sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)[:10]
        print(f"\nТоп-10 адресов по оценке:")
        for i, result in enumerate(sorted_results, 1):
            print(f"  {i}. {result['address']} (score: {result['score']})")
            patterns_str = ", ".join([f"{p['type']}:{p['pattern']}" for p in result["patterns"]])
            print(f"     Паттерны: {patterns_str}")


def main():
    parser = argparse.ArgumentParser(description='Поиск красивых TRON адресов')
    parser.add_argument('--directory', '-d', default=os.path.join(BASE_DIR, "addresses"), 
                       help='Директория для поиска файлов с адресами')
    parser.add_argument('--pattern', '-p', default='addresses*.txt',
                       help='Шаблон имени файлов (по умолчанию: addresses*.txt)')
    parser.add_argument('--min-score', '-s', type=int, default=50,
                       help='Минимальная оценка для красивого адреса (по умолчанию: 50)')
    parser.add_argument('--output', '-o', default='beautiful_addresses.txt',
                       help='Имя выходного файла')
    parser.add_argument('--filter-type', '-t',
                       help='Фильтр по типу паттерна (например: repeating_digits, word)')
    parser.add_argument('--filter-word', '-w',
                       help='Фильтр по наличию слова в адресе')
    parser.add_argument('--scan-file', '-f',
                       help='Сканировать конкретный файл вместо директории')
    
    args = parser.parse_args()
    
    # Создаем экземпляры классов
    matcher = PatternMatcher()
    finder = AddressFinder(matcher)
    
    # Сканируем файлы
    if args.scan_file:
        results = finder.scan_file(args.scan_file, args.min_score)
    else:
        results = finder.scan_directory(args.directory, args.pattern, args.min_score)
    
    # Применяем фильтры
    if args.filter_type:
        results = finder.filter_by_pattern_type(results, args.filter_type)
        print(f"\nПрименен фильтр по типу паттерна: {args.filter_type}")
    
    if args.filter_word:
        results = finder.filter_by_word(results, args.filter_word)
        print(f"Применен фильтр по слову: {args.filter_word}")
    
    # Выводим сводку
    finder.print_summary(results)
    
    # Сохраняем результаты
    if results:
        finder.save_results(results, args.output)


if __name__ == "__main__":
    main()