import os
from typing import Dict, Any, BinaryIO, List

import requests
from loguru import logger
from requests import Response


class YandexDiskAPI:
    """Класс для отправки запросов к API Яндекс Диска"""

    def __init__(self, token: str, cloud_folder: str) -> None:
        """
        :param token: OAuth токен Яндекс Диска
        :param cloud_folder: Путь к папке в облачном хранилище
        """
        self.token: str = token
        self.cloud_folder: str = cloud_folder
        self.base_url: str = "https://cloud-api.yandex.net/v1/disk"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
    ) -> [Dict[str, Any], int]:
        """
        Метод отправки запроса
        :param method: HTTP-метод запроса
        :param endpoint: Конечная точка API
        :param params: Параметры запроса. По умолчанию None
        :param data: Данные запроса. По умолчанию None
        :return: JSON ответ запроса
        """
        headers: Dict[str, str] = {"Authorization": f"OAuth {self.token}"}
        url: str = f"{self.base_url}{endpoint}"
        response: Response = requests.request(
            method, url, headers=headers, params=params, files=data
        )

        response.raise_for_status()

        if response.text:
            return response.json(), response.status_code

    def synchronize_initial(self, local_folder: str) -> None:
        """
        Метод первичной синхронизации с облаком
        :param local_folder: Путь к локальной папке
        :return: None
        """
        try:
            logger.info(f"Первичная синхронизация папки {local_folder}")

            endpoint: str = f"/resources?path={self.cloud_folder}"
            response: Dict[str, Any] = self._make_request("GET", endpoint)[0]
            files: List[Dict[str, Any]] = response["_embedded"]["items"]
            filenames: List[str] = [file["name"] for file in files]
            for filename in filenames:
                self.delete(filename)

            try:
                local_files: List[str] = [
                    f
                    for f in os.listdir(local_folder)
                    if os.path.isfile(os.path.join(local_folder, f))
                    and f != ".DS_Store"
                ]
                for local_file in local_files:
                    self.load_or_reload(
                        os.path.join(local_folder, local_file), overwrite=False
                    )
            except FileNotFoundError:
                logger.error(f"Ошибка: локальной папки {local_folder} не существует")
        except Exception as e:
            logger.error(f"Ошибка синхронизации {local_folder}: {e}")

    def load_or_reload(self, local_folder: str, overwrite: bool) -> None:
        """
        Объединенный метод загрузки/перезаписи файла
        :param local_folder: Путь к локальной папке
        :param overwrite: Перезаписывать файл или нет
        :return: None
        """
        try:
            endpoint: str = "/resources/upload"
            params: Dict[str, str] = {
                "path": f"{self.cloud_folder}/{os.path.basename(local_folder)}",
                "overwrite": str(overwrite).lower(),
            }
            response: Dict[str, Any] = self._make_request(
                "GET", endpoint, params=params
            )[0]
            upload_link: str = response["href"]
            files: Dict[str, BinaryIO] = {"file": open(local_folder, "rb")}
            requests.put(upload_link, files=files)

            if overwrite:
                logger.info(f"Перезаписан файл {local_folder}")
            else:
                logger.info(f"Загружен файл {local_folder}")

        except Exception as e:
            if overwrite:
                logger.error(f"Ошибка перезаписи {local_folder}: {e}")
            else:
                logger.error(f"Ошибка загрузки {local_folder}: {e}")

    def delete(self, filename: str) -> None:
        """
        Метод удаления файла
        :param filename: Имя файла
        :return: None
        """
        try:
            endpoint: str = f"/resources?path={self.cloud_folder}/{filename}"
            self._make_request("DELETE", endpoint)
            logger.info(f"Удален файл {filename}")

        except Exception as e:
            logger.error(f"Ошибка удалении {filename}: {e}")

    def get_info(self) -> Dict[str, Any]:
        """
        Метод получения информации о хранящихся файлах
        :return: JSON ответ запроса
        """
        try:
            endpoint: str = f"/resources?path={self.cloud_folder}"
            logger.info(f"Получена информация о папке {self.cloud_folder}")
            return self._make_request("GET", endpoint)

        except Exception as e:
            logger.error(
                f"Ошибка получения информации о папке {self.cloud_folder}: {e}"
            )
