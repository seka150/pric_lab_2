
import csv
from pathlib import Path


FIELDS = [
    "category",
    "title",
    "audio_url",
    "absolute_path",
    "relative_path"
]


def save_annotation(
    records: list[dict[str, str]],
    annotation_path: Path
) -> None:
    """
    Сохраняет информацию о скачанных аудиофайлах в CSV-аннотацию.

    Создаёт родительские папки для файла аннотации, если они
    отсутствуют. Открывает CSV-файл для записи, создаёт объект
    DictWriter для формирования строк на основе словарей,
    записывает заголовки столбцов и добавляет информацию
    обо всех скачанных аудиофайлах.

    Args:
        records (list[dict[str, str]]): Список словарей
            с информацией об аудиофайлах. Каждый словарь
            содержит категорию, название звука, URL файла,
            абсолютный и относительный пути к нему.
        annotation_path (Path): Путь, по которому необходимо
            сохранить CSV-аннотацию.

    Returns:
        None: Функция не возвращает значение.
    """

    annotation_path.parent.mkdir(parents=True, exist_ok=True)

    with open(
        annotation_path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS
        )

        writer.writeheader()
        writer.writerows(records)
