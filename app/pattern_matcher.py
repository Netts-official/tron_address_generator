#!/usr/bin/env python3
import re
from typing import List, Dict, Tuple, Optional
import json
import os

class PatternMatcher:
    """Класс для проверки адресов на соответствие красивым паттернам"""
    
    def __init__(self, patterns_file: Optional[str] = None):
        self.patterns = {}
        if patterns_file and os.path.exists(patterns_file):
            with open(patterns_file, 'r', encoding='utf-8') as f:
                self.patterns = json.load(f)
        else:
            self.patterns = self.default_patterns()
    
    def default_patterns(self) -> Dict[str, Dict]:
        """Возвращает паттерны по умолчанию"""
        return {
            "repeating_digits": {
                "name": "Повторяющиеся цифры",
                "description": "Адреса с повторяющимися цифрами (например, 8888888)",
                "priority": 1
            },
            "repeating_letters": {
                "name": "Повторяющиеся буквы",
                "description": "Адреса с повторяющимися буквами (например, AAAAAAA)",
                "priority": 2
            },
            "sequential_digits": {
                "name": "Последовательные цифры",
                "description": "Адреса с последовательными цифрами (123456, 654321)",
                "priority": 3
            },
            "words": {
                "name": "Слова в адресе",
                "description": "Адреса, содержащие читаемые слова",
                "priority": 4
            },
            "mirror": {
                "name": "Зеркальные адреса",
                "description": "Адреса с зеркальными частями (например, ABC...CBA)",
                "priority": 5
            },
            "special_ending": {
                "name": "Специальное окончание",
                "description": "Адреса с особыми окончаниями (000, 777, 888)",
                "priority": 6
            },
            "special_beginning": {
                "name": "Специальное начало",
                "description": "Адреса с особыми началами (после префикса T)",
                "priority": 7
            }
        }
    
    def check_repeating_digits(self, address: str, min_length: int = 5) -> List[Tuple[str, int, int]]:
        """Проверяет наличие повторяющихся цифр"""
        results = []
        pattern = r'(\d)\1{' + str(min_length-1) + ',}'
        for match in re.finditer(pattern, address):
            results.append((match.group(), match.start(), match.end()))
        return results
    
    def check_repeating_letters(self, address: str, min_length: int = 5) -> List[Tuple[str, int, int]]:
        """Проверяет наличие повторяющихся букв"""
        results = []
        pattern = r'([A-Za-z])\1{' + str(min_length-1) + ',}'
        for match in re.finditer(pattern, address):
            results.append((match.group(), match.start(), match.end()))
        return results
    
    def check_sequential_digits(self, address: str, min_length: int = 5) -> List[Tuple[str, int, int]]:
        """Проверяет наличие последовательных цифр"""
        results = []
        
        # Проверяем возрастающие последовательности
        for i in range(len(address) - min_length + 1):
            segment = address[i:i+min_length]
            if segment.isdigit():
                is_sequential = True
                for j in range(1, len(segment)):
                    if int(segment[j]) != int(segment[j-1]) + 1:
                        is_sequential = False
                        break
                if is_sequential:
                    results.append((segment, i, i+min_length))
        
        # Проверяем убывающие последовательности
        for i in range(len(address) - min_length + 1):
            segment = address[i:i+min_length]
            if segment.isdigit():
                is_sequential = True
                for j in range(1, len(segment)):
                    if int(segment[j]) != int(segment[j-1]) - 1:
                        is_sequential = False
                        break
                if is_sequential:
                    results.append((segment, i, i+min_length))
        
        return results
    
    def check_words(self, address: str, words: List[str] = None) -> List[Tuple[str, int, int]]:
        """Проверяет наличие слов в адресе"""
        if words is None:
            words = [
                "TRON", "COIN", "CASH", "GOLD", "BANK", "RICH", "MEGA", "SUPER",
                "LUCKY", "HAPPY", "MONEY", "CRYPTO", "WALLET", "FORTUNE", "DIAMOND",
                "CROWN", "KING", "QUEEN", "POWER", "SMART", "FAST", "COOL", "BEST",
                "LOVE", "LIFE", "MOON", "STAR", "SUN", "FIRE", "ICE", "LION",
                "TIGER", "DRAGON", "PHOENIX", "EAGLE", "BEAR", "BULL", "WOLF"
            ]
        
        results = []
        address_upper = address.upper()
        for word in words:
            word_upper = word.upper()
            start = 0
            while True:
                pos = address_upper.find(word_upper, start)
                if pos == -1:
                    break
                results.append((word_upper, pos, pos + len(word_upper)))
                start = pos + 1
        
        return results
    
    def check_mirror(self, address: str, min_length: int = 3) -> List[Tuple[str, str, int, int]]:
        """Проверяет зеркальные паттерны в адресе"""
        results = []
        # Проверяем только часть после префикса 'T'
        if address.startswith('T'):
            addr_part = address[1:]
            for length in range(min_length, min(10, len(addr_part)//2 + 1)):
                start_part = addr_part[:length]
                end_part = addr_part[-length:]
                if start_part == end_part[::-1]:
                    results.append((start_part, end_part, 1, len(address)))
        return results
    
    def check_special_ending(self, address: str, endings: List[str] = None) -> List[Tuple[str, int]]:
        """Проверяет специальные окончания"""
        if endings is None:
            endings = ["000", "111", "222", "333", "444", "555", "666", "777", "888", "999",
                      "0000", "1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888", "9999",
                      "00000", "11111", "22222", "33333", "44444", "55555", "66666", "77777", "88888", "99999",
                      "123", "1234", "12345", "123456", "7777777", "8888888", "777777777", "888888888"]
        
        results = []
        for ending in endings:
            if address.endswith(ending):
                results.append((ending, len(address) - len(ending)))
        return results
    
    def check_special_beginning(self, address: str, beginnings: List[str] = None) -> List[Tuple[str, int]]:
        """Проверяет специальные начала (после префикса T)"""
        if beginnings is None:
            beginnings = ["111", "222", "333", "444", "555", "666", "777", "888", "999",
                         "1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888", "9999",
                         "123", "1234", "12345"]
        
        results = []
        if address.startswith('T') and len(address) > 1:
            addr_part = address[1:]
            for beginning in beginnings:
                if addr_part.startswith(beginning):
                    results.append((beginning, 1))
        return results
    
    def analyze_address(self, address: str) -> Dict[str, any]:
        """Полный анализ адреса на все паттерны"""
        analysis = {
            "address": address,
            "score": 0,
            "patterns_found": []
        }
        
        # Проверяем повторяющиеся цифры
        repeating_digits = self.check_repeating_digits(address)
        if repeating_digits:
            for pattern, start, end in repeating_digits:
                analysis["patterns_found"].append({
                    "type": "repeating_digits",
                    "pattern": pattern,
                    "position": f"{start}-{end}",
                    "score": len(pattern) * 10
                })
                analysis["score"] += len(pattern) * 10
        
        # Проверяем повторяющиеся буквы
        repeating_letters = self.check_repeating_letters(address)
        if repeating_letters:
            for pattern, start, end in repeating_letters:
                analysis["patterns_found"].append({
                    "type": "repeating_letters",
                    "pattern": pattern,
                    "position": f"{start}-{end}",
                    "score": len(pattern) * 8
                })
                analysis["score"] += len(pattern) * 8
        
        # Проверяем последовательные цифры
        sequential = self.check_sequential_digits(address)
        if sequential:
            for pattern, start, end in sequential:
                analysis["patterns_found"].append({
                    "type": "sequential_digits",
                    "pattern": pattern,
                    "position": f"{start}-{end}",
                    "score": len(pattern) * 12
                })
                analysis["score"] += len(pattern) * 12
        
        # Проверяем слова
        words = self.check_words(address)
        if words:
            for word, start, end in words:
                analysis["patterns_found"].append({
                    "type": "word",
                    "pattern": word,
                    "position": f"{start}-{end}",
                    "score": len(word) * 15
                })
                analysis["score"] += len(word) * 15
        
        # Проверяем зеркальные паттерны
        mirrors = self.check_mirror(address)
        if mirrors:
            for start_part, end_part, _, _ in mirrors:
                analysis["patterns_found"].append({
                    "type": "mirror",
                    "pattern": f"{start_part}...{end_part}",
                    "score": len(start_part) * 20
                })
                analysis["score"] += len(start_part) * 20
        
        # Проверяем специальные окончания
        special_endings = self.check_special_ending(address)
        if special_endings:
            for ending, pos in special_endings:
                analysis["patterns_found"].append({
                    "type": "special_ending",
                    "pattern": ending,
                    "position": f"ending at {pos}",
                    "score": len(ending) * 10
                })
                analysis["score"] += len(ending) * 10
        
        # Проверяем специальные начала
        special_beginnings = self.check_special_beginning(address)
        if special_beginnings:
            for beginning, pos in special_beginnings:
                analysis["patterns_found"].append({
                    "type": "special_beginning",
                    "pattern": beginning,
                    "position": f"starting at {pos}",
                    "score": len(beginning) * 10
                })
                analysis["score"] += len(beginning) * 10
        
        return analysis
    
    def is_beautiful(self, address: str, min_score: int = 50) -> bool:
        """Проверяет, является ли адрес красивым (score >= min_score)"""
        analysis = self.analyze_address(address)
        return analysis["score"] >= min_score


if __name__ == "__main__":
    # Тестирование
    matcher = PatternMatcher()
    
    test_addresses = [
        "TQwerty8888888xyz",
        "T123456789abcdef",
        "TaaaaaaBBBBBBccc",
        "TGOLDenCRYPTOabc",
        "Tabcdef123fedcba",
        "Txyz777777777",
        "T888startxyzend"
    ]
    
    for addr in test_addresses:
        analysis = matcher.analyze_address(addr)
        print(f"\nАдрес: {addr}")
        print(f"Оценка: {analysis['score']}")
        print(f"Красивый: {'Да' if matcher.is_beautiful(addr) else 'Нет'}")
        for pattern in analysis['patterns_found']:
            print(f"  - {pattern['type']}: {pattern['pattern']} (score: {pattern['score']})")