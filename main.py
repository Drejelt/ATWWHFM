from download import download_videos_from_json
from parse_subtitles import parse_all_vtt_in_directory, save_subtitles_as_text
from prepare_data import create_vocab_from_texts, create_mappings
from train_model import train_kaldi_model

def main():
    # Шаг 1: Скачиваем видео и субтитры
    download_videos_from_json('links.json', 'downloads')

    # Шаг 2: Парсим субтитры и сохраняем их в текстовом формате
    subtitles_data = parse_all_vtt_in_directory('downloads')
    for video_id, subtitles in subtitles_data.items():
        save_subtitles_as_text(subtitles, f'training_data/{video_id}.txt')

    # Шаг 3: Создаём словарь и маппинг
    create_vocab_from_texts('training_data')
    create_mappings('downloads', 'training_data')

    # Шаг 4: Обучаем модель Vosk
    train_kaldi_model()

if __name__ == "__main__":
    main()
