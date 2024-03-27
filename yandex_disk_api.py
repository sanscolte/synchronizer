import os
from typing import Dict, Any, BinaryIO

import requests

from dotenv_reader import read_env


class YandexDiskAPI:
    """ Класс для отправки запросов к API Яндекс Диска """
    def __init__(self, token: str, folder_path: str) -> None:
        """
        :param token: OAuth токен Яндекс Диска
        :param folder_path: Путь к папке в облачном хранилище
        """
        self.token: str = token
        self.folder_path: str = folder_path
        self.base_url: str = "https://cloud-api.yandex.net/v1/disk"

    def _make_request(
            self, method: str, endpoint: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
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
        response = requests.request(method, url, headers=headers, params=params, data=data)
        print(response)
        response.raise_for_status()  # Raise an exception for bad response status
        return response.json()

    def synchronize_initial(self, local_path: str):
        """

        :return:
        """
        endpoint: str = f"/resources?path={self.folder_path}"
        response = self._make_request("GET", endpoint)
        files = response["_embedded"]["items"]
        filenames = [file["name"] for file in files]

        for filename in filenames:
            self.delete(filename)

        local_files = [f for f in os.listdir(local_path) if os.path.isfile(os.path.join(local_path, f))]
        print(local_files)
        for local_file in local_files:
            self.load_or_reload(os.path.join(local_path, local_file), overwrite=True)

    def load_or_reload(self, local_path: str, overwrite: bool) -> None:
        """
        Объединенный метод загрузки/перезаписи файла
        :param local_path: Путь к локальному файлу
        :param overwrite: Перезаписывать файл или нет
        :return: None
        """
        endpoint: str = "/resources/upload"
        params: Dict[str, str] = {
            "path": f"{self.folder_path}/{os.path.basename(local_path)}",
            "overwrite": str(overwrite).lower()
        }
        files: Dict[str, BinaryIO] = {"file": open(local_path, "rb")}
        print(files)
        self._make_request("POST", endpoint, params=params, data=files)

    def delete(self, filename: str) -> None:
        """
        Метод удаления файла
        :param filename: Имя файла
        :return: None
        """
        endpoint: str = f"/resources?path={self.folder_path}/{filename}"
        self._make_request("DELETE", endpoint)

    def get_info(self) -> Dict[str, Any]:
        """
        Метод получения информации о хранящихся файлах
        :return: JSON ответ запроса
        """
        endpoint: str = f"/resources?path={self.folder_path}"
        return self._make_request("GET", endpoint)


envs = read_env()
token = envs["YANDEX_DISK_TOKEN"]
folder = envs["CLOUD_FOLDER"]
api = YandexDiskAPI(token, folder)
# print(api.get_info())
# api.synchronize_initial('/Users/timofey/Новая папка')
api.load_or_reload('/Users/timofey/new_folder/chatgpt_code.txt', overwrite=True)
