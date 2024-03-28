import os
import unittest
from typing import Dict
from unittest.mock import MagicMock, patch

from yandex_disk_api import YandexDiskAPI


class YandexDiskAPITestCase(unittest.TestCase):
    """Класс тестов API"""

    def setUp(self):
        token: str = os.getenv("YANDEX_DISK_TOKEN")
        cloud_folder: str = os.getenv("CLOUD_FOLDER")
        sync_folder: str = os.getenv("SYNCHRONIZED_FOLDER")

        self.sync_path: str = sync_folder
        self.token: str = token
        self.cloud_folder: str = cloud_folder
        self.api: YandexDiskAPI = YandexDiskAPI(
            token=self.token, cloud_folder=self.cloud_folder
        )

    @patch("yandex_disk_api.YandexDiskAPI._make_request")
    def test_get_info(self, mock_make_request: MagicMock):
        """Тесты получения информации"""
        expected_status_code: int = 200
        mock_make_request.return_value = ({}, expected_status_code)

        api: YandexDiskAPI = self.api
        _, status_code = api.get_info()

        self.assertEqual(status_code, expected_status_code)
        mock_make_request.assert_called_once_with(
            "GET", f"/resources?path={self.cloud_folder}"
        )

    @patch("yandex_disk_api.YandexDiskAPI._make_request")
    def test_delete(self, mock_make_request: MagicMock):
        """Тесты удаления файла"""
        expected_status_code: int = 204
        mock_make_request.return_value = ({}, expected_status_code)
        filename: str = "testfile.txt"

        api: YandexDiskAPI = self.api
        api.delete(filename)

        expected_endpoint: str = f"/resources?path={self.cloud_folder}/{filename}"
        mock_make_request.assert_called_once_with("DELETE", expected_endpoint)

        _, status_code = mock_make_request.return_value
        self.assertEqual(status_code, expected_status_code)

    @patch("yandex_disk_api.YandexDiskAPI._make_request")
    def test_load(self, mock_make_request: MagicMock):
        """Тесты загрузки файла"""
        expected_status_code: int = 200
        expected_json: Dict[str, str] = {"href": ""}
        mock_make_request.return_value = (expected_json, expected_status_code)

        api: YandexDiskAPI = self.api
        api.load_or_reload(self.sync_path, False)
        json, status_code = mock_make_request.return_value

        self.assertEqual(status_code, expected_status_code)
        self.assertIn("href", json)

    @patch("yandex_disk_api.YandexDiskAPI._make_request")
    def test_reload(self, mock_make_request: MagicMock):
        """Тесты перезаписи файла"""
        expected_status_code: int = 200
        expected_json: Dict[str, str] = {"href": ""}
        mock_make_request.return_value = (expected_json, expected_status_code)

        api: YandexDiskAPI = self.api
        api.load_or_reload(self.sync_path, True)
        json, status_code = mock_make_request.return_value

        self.assertEqual(status_code, expected_status_code)
        self.assertIn("href", json)
