import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


URL = "https://sound-effects.ru/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_categories() -> dict[str, str]:
    """
    Получает список категорий с главной страницы сайта.

    Отправляет GET-запрос на сайт, получает HTML-код страницы,
    находит все ссылки на категории и извлекает их названия.
    Формирует словарь, в котором URL категории является ключом,
    а её название — значением.

    Returns:
        dict[str, str]: Словарь, содержащий URL категорий и их названия.
    """

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=(15, 30)
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    categories = {}

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if "/category/" in href:
            category_url = urljoin(URL, href)
            category_name = link.get_text(strip=True)

            if category_name:
                categories[category_url] = category_name

    return categories



def get_least_downloaded_track(category_url: str) -> dict[str, str]:
    """
    Получает звук с наименьшим количеством скачиваний в категории.

    Отправляет GET-запрос на страницу категории с параметром сортировки
    по возрастанию количества скачиваний. Получает HTML-код страницы,
    находит карточки звуков и извлекает информацию о первом звуке.
    При возникновении ошибки запроса повторяет попытку до трёх раз.

    Args:
        category_url (str): URL страницы категории.

    Returns:
        dict[str, str]: Словарь, содержащий идентификатор звука,
        его название и полный URL аудиофайла.

    Raises:
        ValueError: Если в категории нет звуков или не удалось получить
        название либо адрес аудиофайла.
        requests.RequestException: Если не удалось получить страницу
        после трёх попыток.
    """ 

    for attempt in range(3):
        try:
            response = requests.get(
                category_url,
                params={"select": "ndownloadlow"},
                headers=HEADERS,
                timeout=(15, 30)
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            tracks = soup.find_all("div", class_="onetrack")

            if not tracks:
                raise ValueError(
                    f"В категории нет доступных звуков: {category_url}"
                )

            track = tracks[0]

            title_element = track.find("div", class_="waveTitle")
            if title_element is None:
                raise ValueError("Не удалось получить название звука.")

            title = title_element.get_text(strip=True)
            audio_path = track.get("data-track")
            track_id = track.get("data-id")

            if not audio_path:
                raise ValueError("Не удалось получить адрес аудиофайла.")

            audio_url = urljoin(category_url, audio_path)

            return {
                "id": track_id or "",
                "title": title,
                "audio_url": audio_url
            }

        except requests.RequestException:
            if attempt == 2:
                raise
            print(f"Повторная попытка {attempt + 2}/3...")
