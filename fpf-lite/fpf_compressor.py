#!/usr/bin/env python3

import re
import os

def normalize_text(text):
    """
    Заменяет все виды тире, дефисов и неразрывных пробелов на стандартные ASCII символы.
    Это критично для FPF, где используется '‑' (U+2011) вместо '-'.
    """
    text = text.replace('\u2011', '-') # Non-breaking hyphen
    text = text.replace('\u2013', '-') # En dash
    text = text.replace('\u2014', '-') # Em dash
    text = text.replace('\u00A0', ' ') # Non-breaking space
    return text

def compress_fpf(input_path, output_path, aggressive=False):
    # Ключевые слова для удаления. 
    # Пишем их с ОБЫЧНЫМ дефисом, так как текст мы нормализуем перед проверкой.
    REMOVE_KEYWORDS = [
        "SoTA-Echoing", 
        "SOTA-Echoing",
        "State-of-the-Art",
        "SoTA echoing"
    ]
    
    if aggressive:
        REMOVE_KEYWORDS.extend([
            "Problem frame", 
            "Problem", 
            "Forces", 
            "Rationale",
            "Anti-patterns" # Опционально, если нужно сэкономить еще
        ])

    # Паттерн заголовка Markdown (от 1 до 6 решеток)
    header_pattern = re.compile(r'^(#+)\s+(.*)')
    
    # Паттерн начала "полезной нагрузки" (пропускаем Preface)
    # Ищем начало "Part A" или "A.0"
    start_marker_pattern = re.compile(r'^#+\s+(Part A|A\.0)', re.IGNORECASE)

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Файл {input_path} не найден.")
        return

    output_lines = []
    
    # Флаги состояния
    is_content_started = False
    skipping_section = False
    skip_level = 0
    
    removed_counters = {k: 0 for k in REMOVE_KEYWORDS}
    
    print(f"Обработка {len(lines)} строк...")

    for line in lines:
        # 1. Логика удаления Preface (всего до Part A)
        if not is_content_started:
            if start_marker_pattern.match(line):
                is_content_started = True
                output_lines.append(line)
                print("--> Найдено начало контента (Part A/A.0). Preface удален.")
                continue
            else:
                continue # Пропускаем строки Preface

        # 2. Проверка заголовков
        match = header_pattern.match(line)
        if match:
            level = len(match.group(1)) # Уровень заголовка (#)
            raw_title = match.group(2).strip()
            
            # Нормализуем заголовок для проверки (убираем спец. символы)
            clean_title = normalize_text(raw_title)

            # Если мы сейчас пропускаем секцию...
            if skipping_section:
                # Если встретили заголовок того же уровня или выше (меньше #) -> конец пропуска
                if level <= skip_level:
                    skipping_section = False
                else:
                    # Это подсекция -> продолжаем пропускать
                    continue

            # Проверяем, нужно ли удалить эту новую секцию
            found_keyword = None
            for keyword in REMOVE_KEYWORDS:
                # Проверка: ищем ключевое слово в нормализованном заголовке
                if keyword.lower() in clean_title.lower():
                    found_keyword = keyword
                    break
            
            if found_keyword and not skipping_section:
                skipping_section = True
                skip_level = level
                removed_counters[found_keyword] += 1
                # print(f"  [Удалено] {raw_title}") # Раскомментируйте для отладки
                continue

        # 3. Запись строки (если не в режиме пропуска)
        if not skipping_section:
            output_lines.append(line)

    # Сохранение
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

    print("-" * 30)
    print(f"Статистика удалений секций:")
    for k, v in removed_counters.items():
        if v > 0:
            print(f"  - {k}: {v} шт.")
    
    original_size = len(lines)
    new_size = len(output_lines)
    reduction = round((1 - new_size/original_size)*100, 1)
    
    print("-" * 30)
    print(f"Готово. Результат: {output_path}")
    print(f"Строк: {original_size} -> {new_size} (сжатие {reduction}%)")
    print()

if __name__ == "__main__":
    INPUT_FILE = "FPF-Spec.md"
        
    compress_fpf(INPUT_FILE, "FPF-Spec-Lite.md", False)
    compress_fpf(INPUT_FILE, "FPF-Spec-Aggressive.md", True)