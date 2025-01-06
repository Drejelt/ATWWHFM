import os
import subprocess


def prepare_kaldi_data(text_dir, audio_dir):
    """Подготавливает данные для Kaldi в необходимом формате."""
    # Создаём директорию для Kaldi данных
    kaldi_dir = 'kaldi_data'
    if not os.path.exists(kaldi_dir):
        os.makedirs(kaldi_dir)

    # Записываем wav.scp (список аудиофайлов)
    with open(os.path.join(kaldi_dir, 'wav.scp'), 'w', encoding='utf-8') as wav_scp_file:
        for audio_file in os.listdir(audio_dir):
            if audio_file.endswith('.wav'):
                audio_path = os.path.join(audio_dir, audio_file)
                wav_scp_file.write(f"{audio_file} {audio_path}\n")

    # Записываем text (список текстов/транскриптов)
    with open(os.path.join(kaldi_dir, 'text'), 'w', encoding='utf-8') as text_file:
        for txt_file in os.listdir(text_dir):
            if txt_file.endswith('.txt'):
                with open(os.path.join(text_dir, txt_file), 'r', encoding='utf-8') as file:
                    text = file.read().strip()
                    utt_id = os.path.splitext(txt_file)[0]  # ID - это имя без расширения
                    text_file.write(f"{utt_id} {text}\n")

    # Записываем utt2spk (идентификаторы говорящего)
    with open(os.path.join(kaldi_dir, 'utt2spk'), 'w', encoding='utf-8') as utt2spk_file:
        for audio_file in os.listdir(audio_dir):
            if audio_file.endswith('.wav'):
                utt_id = os.path.splitext(audio_file)[0]
                utt2spk_file.write(f"{utt_id} speaker_1\n")  # Можно использовать одну метку говорящего

    # Записываем spk2utt (обратное соответствие от говорящего к файлам)
    with open(os.path.join(kaldi_dir, 'spk2utt'), 'w', encoding='utf-8') as spk2utt_file:
        spk2utt_file.write("speaker_1 " + " ".join(
            [os.path.splitext(file)[0] for file in os.listdir(audio_dir) if file.endswith('.wav')]) + "\n")

    print(f"Kaldi данные подготовлены в директории {kaldi_dir}.")


def train_kaldi_model():
    """Запускает обучение модели с использованием Kaldi."""
    kaldi_dir = 'kaldi_data'

    # Проверка, что данные подготовлены
    if not os.path.exists(os.path.join(kaldi_dir, 'wav.scp')):
        print("Ошибка: Не найдены подготовленные данные для Kaldi.")
        return

    # Запуск обучения
    print("Запуск процесса обучения модели с использованием Kaldi...")

    # 1. Настройка переменных Kaldi
    kaldi_root = '/path/to/kaldi'  # Укажите путь к установленному Kaldi
    cmd = f"export KALDI_ROOT={kaldi_root} && source $KALDI_ROOT/tools/env.sh"

    # 2. Запуск процесса обучения
    # Для простоты, будем использовать стандартные скрипты Kaldi для обучения.
    training_cmd = f"""
    cd {kaldi_root}/egs/your_project_dir
    ./run.sh --data-dir {kaldi_dir} --exp-dir exp
    """

    try:
        # Выполнение команды
        subprocess.run(cmd, shell=True, check=True)
        subprocess.run(training_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при обучении модели: {e}")

    print("Процесс обучения завершён.")


def main():
    # Подготовка данных
    prepare_kaldi_data('training_data', 'downloads')

    # Обучение модели
    train_kaldi_model()


if __name__ == "__main__":
    main()
