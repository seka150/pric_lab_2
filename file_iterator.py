
import csv
from pathlib import Path


class AudioFileIterator:
    """
    Итератор для последовательного получения путей к аудиофайлам.

    Поддерживает два источника данных: CSV-файл с информацией
    об аудиофайлах или папку, содержащую аудиофайлы.
    При загрузке проверяет существование файлов и их расширения.
    Возвращает пути к аудиофайлам по одному за раз.

    Attributes:
        AUDIO_EXTENSIONS (set[str]): Множество поддерживаемых
            расширений аудиофайлов.
        source (Path): Путь к исходной папке или CSV-файлу.
        files (list[Path]): Список найденных аудиофайлов.
        index (int): Индекс следующего файла для получения.
    """

    AUDIO_EXTENSIONS = {
        ".mp3",
        ".wav",
        ".ogg",
        ".flac"
    }

    def __init__(self, source: str | Path):
        """
        Инициализирует итератор и загружает пути к аудиофайлам.

        Определяет тип источника данных. Если источник является
        папкой, загружает аудиофайлы из неё и её вложенных папок.
        Если источник является CSV-файлом, извлекает пути
        к аудиофайлам из его записей.

        Args:
            source (str | Path): Путь к папке с аудиофайлами
                или к CSV-файлу с их описанием.

        Raises:
            ValueError: Если источник не является существующей
                папкой или CSV-файлом.
        """
        self.source = Path(source)
        self.files = []
        self.index = 0

        if self.source.is_dir():
            self._load_from_directory()

        elif self.source.is_file() and self.source.suffix.lower() == ".csv":
            self._load_from_csv()

        else:
            raise ValueError(
                "Источник должен быть папкой или CSV-файлом."
            )

    def _load_from_directory(self) -> None:
        """
        Загружает аудиофайлы из указанной папки.

        Рекурсивно обходит исходную папку и все её вложенные папки.
        Отбирает существующие файлы с поддерживаемыми расширениями,
        преобразует их пути в абсолютные и добавляет в список files.

        Returns:
            None: Метод не возвращает значение.
        """

        for file_path in sorted(self.source.rglob("*")):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.AUDIO_EXTENSIONS
            ):
                self.files.append(file_path.resolve())

    def _load_from_csv(self) -> None:
        """
        Загружает пути к аудиофайлам из CSV-файла.

        Читает CSV-файл с помощью DictReader и для каждой записи
        получает абсолютный или относительный путь к аудиофайлу.
        Проверяет существование файла и его расширение.
        Подходящие пути преобразует в абсолютные и добавляет
        в список files.

        Returns:
            None: Метод не возвращает значение.
        """

        with open(
            self.source,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                absolute_path = row.get("absolute_path", "")
                relative_path = row.get("relative_path", "")

                if absolute_path:
                    file_path = Path(absolute_path)
                elif relative_path:
                    file_path = self.source.parent / relative_path
                else:
                    continue

                if (
                    file_path.is_file()
                    and file_path.suffix.lower() in self.AUDIO_EXTENSIONS
                ):
                    self.files.append(file_path.resolve())

    def __iter__(self):
        """
        Возвращает объект итератора и сбрасывает его позицию.

        Устанавливает индекс текущего файла в ноль, чтобы
        перебор аудиофайлов начинался с первого элемента.

        Returns:
            AudioFileIterator: Текущий объект итератора.
        """
        self.index = 0
        return self

    def __next__(self) -> Path:
        """
        Возвращает путь к следующему аудиофайлу.

        Получает файл по текущему индексу, увеличивает индекс
        на единицу и возвращает путь к найденному файлу.
        Если все файлы уже обработаны, завершает итерацию.

        Returns:
            Path: Абсолютный путь к следующему аудиофайлу.

        Raises:
            StopIteration: Если все аудиофайлы уже перебраны.
        """
        if self.index >= len(self.files):
            raise StopIteration

        file_path = self.files[self.index]
        self.index += 1

        return file_path
