
import argparse
from pathlib import Path

import requests

from parser import get_categories, get_least_downloaded_track
from downloader import download_track
from annotation import save_annotation
from file_iterator import AudioFileIterator


def parse_arguments() -> argparse.Namespace:
    """
    Получает и проверяет аргументы командной строки.

    Создаёт парсер аргументов, определяет настройки программы,
    которые пользователь должен указать при запуске, получает
    их значения и проверяет корректность количества категорий.

    Returns:
        argparse.Namespace: Объект с настройками программы:
        номером варианта, количеством категорий, путём к папке
        для сохранения файлов и путём к CSV-аннотации.

    Raises:
        SystemExit: Если обязательные аргументы не указаны
        или количество категорий меньше либо равно нулю.
    """

    parser = argparse.ArgumentParser(
        description="Скачивание звуков с сайта sound-effects.ru"
    )

    parser.add_argument(
        "--variant",
        type=int,
        required=True,
        help="Номер варианта"
    )

    parser.add_argument(
        "--categories",
        type=int,
        required=True,
        help="Количество категорий для обработки"
    )

    parser.add_argument(
        "--save-dir",
        type=Path,
        required=True,
        help="Папка для сохранения аудиофайлов"
    )

    parser.add_argument(
        "--annotation",
        type=Path,
        required=True,
        help="Путь к CSV-аннотации"
    )

    args = parser.parse_args()

    if args.categories <= 0:
        parser.error("Количество категорий должно быть больше нуля.")

    return args


def main() -> None:
    """
    Запускает основной процесс скачивания аудиофайлов.

    Получает настройки из командной строки, загружает список
    категорий сайта и обрабатывает указанное пользователем
    количество категорий. Для каждой категории находит звук
    с наименьшим количеством скачиваний, скачивает его,
    сохраняет информацию о файле в список записей.
    После обработки категорий создаёт CSV-аннотацию,
    выводит результаты работы и проверяет собственный
    итератор по аудиофайлам.

    Args:
        Нет аргументов.

    Returns:
        None: Функция не возвращает значение.
    """

    args = parse_arguments()

    print(f"Вариант: {args.variant}")
    print("Получение категорий сайта...")

    categories = get_categories()

    print(f"Найдено категорий: {len(categories)}")

    if args.categories > len(categories):
        raise ValueError(
            "Запрошено больше категорий, чем найдено на сайте."
        )

    selected_categories = list(categories.items())[:args.categories]

    records = []
    successful_downloads = 0

    for category_url, category_name in selected_categories:
        print(f"\nКатегория: {category_name}")

        try:
            track = get_least_downloaded_track(category_url)

            print(f"Звук: {track['title']}")

            file_path = download_track(
                track,
                args.save_dir,
                successful_downloads + 1
            )

            save_dir = args.save_dir.resolve()

            relative_path = file_path.relative_to(save_dir)

            record = {
                "category": category_name,
                "title": track["title"],
                "audio_url": track["audio_url"],
                "absolute_path": str(file_path),
                "relative_path": str(relative_path)
            }

            records.append(record)
            successful_downloads += 1

            print(f"Скачан: {file_path.name}")

        except (requests.RequestException, ValueError, OSError) as error:
            print(f"Не удалось обработать категорию: {error}")

    save_annotation(records, args.annotation)

    print("\nРабота завершена.")
    print(f"Успешно скачано файлов: {successful_downloads}")
    print(f"Аннотация сохранена: {args.annotation.resolve()}")

    print("\nПроверка собственного итератора:")

    iterator = AudioFileIterator(args.annotation)

    for audio_file in iterator:
        print(audio_file)


if __name__ == "__main__":
    main()
