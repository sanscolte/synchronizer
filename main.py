from typing import Dict, Any

from loguru import logger

from dotenv_reader import read_env
from watch_local_folder import watch_local_folder
from yandex_disk_api import YandexDiskAPI
from logger import setup_logger


def main() -> None:
    """
    Основная функция запуска синхронизатора
    :return: None
    """

    # Чтение параметров из файла .env
    env_vars: Dict[str, Any] = read_env()
    token: str = env_vars["YANDEX_DISK_TOKEN"]
    cloud_folder: str = env_vars["CLOUD_FOLDER"]
    sync_folder: str = env_vars["SYNCHRONIZED_FOLDER"]
    log_file: str = env_vars["LOG_FILE"]

    # Настройка логгера
    setup_logger(log_file)
    logger.info(f"Запуск сервиса в папке {sync_folder}")

    # Выполнение первичной синхронизации
    api: YandexDiskAPI = YandexDiskAPI(token=token, cloud_folder=cloud_folder)
    api.synchronize_initial(local_folder=sync_folder)

    # Запуск мониторинга
    watch_local_folder(local_folder=sync_folder, cloud_api=api)


if __name__ == "__main__":
    main()
