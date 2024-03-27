import os
import time

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from yandex_disk_api import YandexDiskAPI


class MyHandler(FileSystemEventHandler):
    """ Класс обработчика """
    def __init__(self, cloud_api: YandexDiskAPI, sync_period: int):
        """
        :param cloud_api: API облачного хранилища
        :param sync_period: Период синхронизации
        """
        super().__init__()
        self.cloud_api = cloud_api
        self.sync_period = sync_period

    def set_sync_period(self, sync_period: int) -> None:
        """
        Установка периода синхронизации
        :param sync_period:
        :return:
        """
        self.sync_period = sync_period

    def on_created(self, event: FileSystemEvent) -> None:
        """
        Метод отслеживания создания файлов
        :param event: FileSystemEvent
        :return: None
        """
        if not event.is_directory:
            local_path: str = event.src_path
            filename: str = os.path.basename(local_path)
            self.cloud_api.load_or_reload(local_path, overwrite=False)
            print(f'File {filename} was created')

    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Метод отслеживания изменения файлов
        :param event: FileSystemEvent
        :return: None
        """
        if not event.is_directory:
            local_path: str = event.src_path
            filename: str = os.path.basename(local_path)
            self.cloud_api.load_or_reload(local_path, overwrite=True)
            print(f'File {filename} was modified')

    def on_deleted(self, event: FileSystemEvent) -> None:
        """
        Метод отслеживания удаления файлов
        :param event: FileSystemEvent
        :return: None
        """
        if not event.is_directory:
            local_path: str = event.src_path
            filename: str = os.path.basename(local_path)
            self.cloud_api.delete(os.path.basename(local_path))
            print(f'File {filename} was deleted')


def watch_local_folder(folder_path: str, yandex_disk_api: YandexDiskAPI, sync_period: int):
    print('Starting up the observer')
    observer: Observer = Observer()
    observer.schedule(MyHandler(cloud_api=yandex_disk_api, sync_period=sync_period), folder_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# if __name__ == '__main__':
#     folder = '/Users/timofey/PycharmProjects/synchronizer'
#     watch_local_folder(folder)
