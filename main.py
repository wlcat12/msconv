# MSConv ver 1.0 - Начало Начал
import os
import subprocess
import shutil
import sys
import urllib.request
import tempfile
import platform

def is_ffmpeg_installed():
    # Проверка на установленный ffmpeg
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except Exception:
        return False

def install_ffmpeg_on_windows():
    # Автоскачивание ffmpeg
    installer_url = "https://github.com/icedterminal/ffmpeg-installer/releases/download/latest/FFmpeg_Essentials.msi"
    print("Начинается автоматическая установка ffmpeg...")

    # Скачивание установщика во временную папку
    tmp_dir = tempfile.gettempdir()
    installer_path = os.path.join(tmp_dir, "FFmpeg_Essentials.msi")
    try:
        print("Скачивание установщика ffmpeg...")
        urllib.request.urlretrieve(installer_url, installer_path)
        print(f"Установщик сохранён: {installer_path}")
    except Exception as e:
        print("Ошибка при скачивании установщика:", e)
        sys.exit(1)

    # Запуск установки с помощью msiexec в тихом режиме (/qn)
    try:
        print("Запуск установки ffmpeg...")
        subprocess.run(["msiexec", "/i", installer_path, "/qn"], check=True)
        print("ffmpeg успешно установлен.")
    except subprocess.CalledProcessError as e:
        print("Ошибка установки ffmpeg:", e)
        sys.exit(1)
    finally:
        # Удаление временного установщика
        try:
            os.remove(installer_path)
        except Exception as e:
            print("Не удалось удалить временный установщик:", e)

def check_ffmpeg():
    # Проверяет наличие ffmpeg. Если ffmpeg не установлен и ОС Windows, то дополнительно проверяется:
    # версия Windows: автоустановка работает только на Windows 7 (6.1) и выше
    # архитектура: допускаются только x86_64/AMD64 или arm64/aarch64.
    # Если условия не выполнены или пользователь отказывается от установки, программа завершается.
    if not is_ffmpeg_installed():
        if platform.system().lower() == "windows":
            # Проверяем версию Windows
            win_ver = sys.getwindowsversion()
            if win_ver.major < 6 or (win_ver.major == 6 and win_ver.minor < 1):
                print(f"Ошибка: ffmpeg не найден. Пожалуйста, установите ffmpeg и добавьте его в PATH. Автоустановка работает только на Windows 7 (6.1) и выше. Ваша система: Windows {win_ver.major}.{win_ver.minor}")
                sys.exit(1)

            # Проверяем архитектуру
            machine = platform.machine().lower()
            allowed_arch = ("x86_64", "amd64", "arm64", "aarch64")
            if machine not in allowed_arch:
                print(f"Автоустановка ffmpeg невозможна для архитектуры: {machine}")
                sys.exit(1)

            if win_ver.major == 10 and machine in ("arm64", "aarch64"):
                print("Ошибка: ffmpeg не найден. Пожалуйста, установите ffmpeg и добавьте его в PATH. Автоустановка ffmpeg не поддерживается на Windows 10 на ARM64")
                sys.exit(1)

            choice = input("ffmpeg не найден. Установить автоматически? (Y/n): ").strip().lower()
            if choice in ("", "y", "yes"):
                install_ffmpeg_on_windows()
            else:
                print("Ошибка: ffmpeg не найден. Пожалуйста, установите ffmpeg и добавьте его в PATH.")
                sys.exit(1)
        else:
            print("Ошибка: ffmpeg не найден. Пожалуйста, установите ffmpeg и добавьте его в PATH.")
            sys.exit(1)
    else:
        print("ffmpeg установлен.")

def clear_output_folder(output_folder):
    if os.path.exists(output_folder):
        # Удаляем все файлы и папки внутри
        for filename in os.listdir(output_folder):
            file_path = os.path.join(output_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                shutil.rmtree(file_path)
    else:
        os.makedirs(output_folder)

def convert_file(input_file, output_file):
    # Конвертация музыки в нужный формат для радио
    # TODO: сделать конвертацию для CD
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-ac", "1",
        "-ar", "22050",
        "-c:a", "libvorbis",
        output_file,
        "-y"
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Конвертирован: {input_file} -> {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при конвертации {input_file}: {e.stderr.decode('utf-8')}")

def main():
    # Проверяем наличие ffmpeg
    check_ffmpeg()

    # Запрос пути к папке с музыкой у пользователя
    # TODO: скачивание плей листов из youtube, а в следствии, добавление нескольких источников сразу
    input_folder = input("Введите путь к папке с музыкой: ").strip()
    if not os.path.exists(input_folder):
        print("Указанная папка не существует.")
        return

    # Определяем папку для результатов
    output_folder = os.path.join("output", "Radio")
    clear_output_folder(output_folder)

    # Здеся все форматы, которые сейчас поддерживаются, можно потом добавить интересующие форматы
    # Сделано для того, что бы не конвертировать ненужные файлы в аудио (например, lnk с десктопа)
    valid_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg']
    files = [f for f in os.listdir(input_folder)
             if os.path.splitext(f)[1].lower() in valid_extensions]
    files.sort()  # сортировка для стабильного порядка

    max_files = 199 # Макс. кол-во музыки на радио
    count = 0

    for file in files:
        if count >= max_files:
            print (f"Треков больше, чем {max_files}" )
            break
        input_file_path = os.path.join(input_folder, file)
        count += 1
        output_file_path = os.path.join(output_folder, f"track{count}.ogg")
        convert_file(input_file_path, output_file_path)

    print("Конвертация завершена.")

if __name__ == "__main__":
    main()
