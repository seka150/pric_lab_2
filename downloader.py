
from pathlib import Path

import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def download_track(
    track: dict[str, str],
    save_dir: Path,
    number: int
) -> Path:
    """
    Скачивает аудиофайл и возвращает путь к нему.

    Создаёт папку для сохранения файла, формирует его имя
    на основе порядкового номера и идентификатора звука.
    Скачивает аудиофайл частями, чтобы не загружать его
    целиком в оперативную память. При ошибке запроса
    удаляет временный файл и повторяет попытку до трёх раз.
    После успешного скачивания переименовывает временный
    файл и возвращает абсолютный путь к нему.

    Args:
        track (dict[str, str]): Словарь с информацией
            об аудиофайле. Должен содержать ключи "id"
            и "audio_url".
        save_dir (Path): Путь к папке, в которую
            необходимо сохранить аудиофайл.
        number (int): Порядковый номер скачиваемого файла.
            Используется при формировании имени файла.

    Returns:
        Path: Абсолютный путь к сохранённому аудиофайлу.

    Raises:
        requests.RequestException: Если не удалось скачать
            аудиофайл после трёх попыток.
        RuntimeError: Если скачивание не удалось завершить.
    """

    save_dir.mkdir(parents=True, exist_ok=True)

    track_id = track["id"] or str(number)

    filename = f"{number:03d}_{track_id}.mp3"
    file_path = save_dir / filename

    temporary_path = file_path.with_suffix(".mp3.part")

    for attempt in range(3):
        try:
            with requests.get(
                track["audio_url"],
                headers=HEADERS,
                stream=True,
                timeout=(15, 90)
            ) as response:

                response.raise_for_status()

                with open(temporary_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)

            temporary_path.replace(file_path)

            return file_path.resolve()

        except requests.RequestException:
            temporary_path.unlink(missing_ok=True)

            if attempt == 2:
                raise

            print(
                f"Ошибка скачивания. "
                f"Повторная попытка {attempt + 2}/3..."
            )

    raise RuntimeError("Не удалось скачать аудиофайл.")
