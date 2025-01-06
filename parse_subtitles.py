import os
import re

def parse_vtt_file(vtt_file):
    """Парсит файл .vtt и извлекает текстовые субтитры."""
    subtitles = []
    with open(vtt_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            # Пропускаем таймкоды и пустые строки
            if '-->' in line or line.strip() == "":
                continue
            # Сохраняем текст субтитров
            subtitles.append(line.strip())
    return subtitles

def parse_all_vtt_in_directory(directory):
    """Парсит все файлы .vtt в указанной директории."""
    subtitles_data = {}
    for filename in os.listdir(directory):
        if filename.endswith('.vtt'):
            video_id = os.path.splitext(filename)[0]
            vtt_file = os.path.join(directory, filename)
            subtitles_data[video_id] = parse_vtt_file(vtt_file)
    return subtitles_data

def save_subtitles_as_text(subtitles, output_file):
    """Сохраняет субтитры в текстовом формате для обучения модели."""
    with open(output_file, 'w', encoding='utf-8') as file:
        for line in subtitles:
            file.write(f"{line}\n")
