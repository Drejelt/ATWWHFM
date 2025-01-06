import yt_dlp
import os
import json


def download_video_and_subtitles(video_url, output_dir="downloads"):
    """Скачивает видео и субтитры с YouTube."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'writeautomaticsub': True,  # Скачиваем автоматические субтитры
        'subtitleslangs': ['en'],  # Указываем язык субтитров
        'subtitlesformat': 'vtt',  # Формат субтитров
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        return os.path.join(output_dir, f"{info['id']}.vtt"), os.path.join(output_dir, f"{info['id']}.wav")


def load_video_links_from_json(json_file='links.json'):
    """Загружает ссылки на видео из JSON файла."""
    if not os.path.exists(json_file):
        print(f"{json_file} не найден. Создаю новый файл с примером...")
        create_json_with_example(json_file)

    with open(json_file, 'r', encoding='utf-8') as file:
        links = json.load(file)
    return links


def create_json_with_example(json_file='links.json'):
    """Создаёт новый JSON файл с примером ссылки на видео."""
    example_data = {
        "__comment": "Вставьте сюда ссылки на видео YouTube.\nПример: https://www.youtube.com/watch?v=video_id",
        "links": [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Пример ссылки на видео
            "https://www.youtube.com/watch?v=video_id_2",  # Вставьте сюда другие ссылки
            "https://www.youtube.com/watch?v=video_id_3"  # Вставьте сюда другие ссылки
        ]
    }

    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(example_data, file, indent=4, ensure_ascii=False)
    print(f"Файл {json_file} был создан с примером.")


def download_videos_from_json(json_file='links.json', output_dir='downloads'):
    """Скачивает видео и субтитры для всех ссылок из JSON файла."""
    links_data = load_video_links_from_json(json_file)
    links = links_data.get("links", [])

    for video_url in links:
        print(f"Downloading {video_url}...")
        subtitles_file, audio_file = download_video_and_subtitles(video_url, output_dir)
        print(f"Downloaded subtitles to {subtitles_file}")
        print(f"Downloaded audio to {audio_file}")
