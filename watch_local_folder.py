import os
import time
from typing import Dict, Any, List

from loguru import logger
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from dotenv_reader import read_env
from yandex_disk_api import YandexDiskAPI

ignored_files: List[str] = [
    ".DS_Store",
]  # файлы, которые хотим игнорировать


class MyHandler(FileSystemEventHandler):
    """Класс обработчика"""

    def __init__(self, cloud_api: YandexDiskAPI):
        """
        :param cloud_api: API облачного хранилища
        """
        super().__init__()
        self.cloud_api = cloud_api

    def on_created(self, event: FileSystemEvent) -> None:
        """
        Метод отслеживания создания файлов
        :param event: FileSystemEvent
        :return: None
        """
        if not event.is_directory:
            local_path: str = event.src_path
            filename: str = os.path.basename(local_path)
            if filename not in ignored_files:
                self.cloud_api.load_or_reload(local_path, overwrite=False)
                print(f"File {filename} was created")
            return

    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Метод отслеживания изменения файлов
        :param event: FileSystemEvent
        :return: None
        """
        if not event.is_directory:
            local_path: str = event.src_path
            filename: str = os.path.basename(local_path)
            if filename not in ignored_files:
                self.cloud_api.load_or_reload(local_path, overwrite=True)
                print(f"File {filename} was modified")
            return

    def on_deleted(self, event: FileSystemEvent) -> None:
        """
        Метод отслеживания удаления файлов
        :param event: FileSystemEvent
        :return: None
        """
        if not event.is_directory:
            local_path: str = event.src_path
            filename: str = os.path.basename(local_path)
            if filename not in ignored_files:
                self.cloud_api.delete(os.path.basename(local_path))
                print(f"File {filename} was deleted")
            return


def watch_local_folder(local_folder: str, cloud_api: YandexDiskAPI) -> None:
    """
    Функция запуска мониторинга папки
    :param local_folder: Путь к локальной папке
    :param cloud_api: API облачного сервиса
    :return: None
    """
    observer: Observer = Observer()
    observer.schedule(MyHandler(cloud_api=cloud_api), local_folder, recursive=False)
    observer.start()

    env_vars: Dict[str, Any] = read_env()
    sync_period: str = env_vars["SYNC_PERIOD"]

    try:
        while True:
            try:
                time.sleep(int(sync_period))
            except ValueError as e:
                logger.error(f"Ошибка периода синхронизации: {e}")
                break
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
