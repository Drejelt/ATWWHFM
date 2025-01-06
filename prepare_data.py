import os


def create_vocab_from_texts(text_files_dir):
    """Создаёт словарь из текстовых файлов с субтитрами."""
    vocab = set()
    for filename in os.listdir(text_files_dir):
        if filename.endswith('.txt'):
            with open(os.path.join(text_files_dir, filename), 'r', encoding='utf-8') as file:
                for line in file:
                    words = line.strip().split()
                    vocab.update(words)

    with open('training_data/vocab.txt', 'w', encoding='utf-8') as file:
        for word in sorted(vocab):
            file.write(f"{word}\n")


def create_mappings(audio_dir, text_dir):
    """Создаёт маппинг между аудиофайлами и текстовыми файлами."""
    mappings = []
    for filename in os.listdir(audio_dir):
        if filename.endswith('.wav'):
            audio_file = os.path.join(audio_dir, filename)
            text_file = os.path.join(text_dir, f"{os.path.splitext(filename)[0]}.txt")
            if os.path.exists(text_file):
                with open(text_file, 'r', encoding='utf-8') as file:
                    text = file.read().strip()
                mappings.append((audio_file, text))

    with open('training_data/mappings.txt', 'w', encoding='utf-8') as file:
        for audio_file, text in mappings:
            file.write(f"{audio_file}|{text}\n")
