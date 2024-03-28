import unittest
from unittest.mock import patch, MagicMock

from watchdog.events import FileSystemEvent

from watch_local_folder import MyHandler


class TestMyHandler(unittest.TestCase):
    """Класс тестов обработчика"""

    def setUp(self):
        self.file_path: str = "/Users/timofey/new_folder/test.txt"
        self.filename: str = "test.txt"

    @patch("watch_local_folder.YandexDiskAPI")
    def test_on_created(self, mock_yandex_disk_api):
        """Тест создания файла"""
        mock_cloud_api = mock_yandex_disk_api()
        handler: MyHandler = MyHandler(mock_cloud_api)

        mock_event: MagicMock = MagicMock(spec=FileSystemEvent)
        mock_event.is_directory = False
        mock_event.src_path = self.file_path

        handler.on_created(mock_event)

        mock_cloud_api.load_or_reload.assert_called_once_with(
            self.file_path, overwrite=False
        )

    @patch("watch_local_folder.YandexDiskAPI")
    def test_on_modified(self, mock_yandex_disk_api):
        """Тест изменения файла"""
        mock_cloud_api = mock_yandex_disk_api()
        handler: MyHandler = MyHandler(mock_cloud_api)

        mock_event: MagicMock = MagicMock(spec=FileSystemEvent)
        mock_event.is_directory = False
        mock_event.src_path = self.file_path

        handler.on_modified(mock_event)

        mock_cloud_api.load_or_reload.assert_called_once_with(
            self.file_path, overwrite=True
        )

    @patch("watch_local_folder.YandexDiskAPI")
    def test_on_deleted(self, mock_yandex_disk_api):
        """Тест удаления файла"""
        mock_cloud_api = mock_yandex_disk_api()
        handler: MyHandler = MyHandler(mock_cloud_api)

        mock_event: MagicMock = MagicMock(spec=FileSystemEvent)
        mock_event.is_directory = False
        mock_event.src_path = self.file_path

        handler.on_deleted(mock_event)

        mock_cloud_api.delete.assert_called_once_with(self.filename)
