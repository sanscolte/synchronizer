from dotenv_reader import read_env
from yandex_disk_api import YandexDiskAPI
from watch_local_folder import watch_local_folder
from logger import setup_logger


def main():
    # Чтение параметров из файла .env
    env_vars = read_env()

    # Настройка логгера
    setup_logger(env_vars['logs.log'])

    # Создание экземпляра класса для работы с Яндекс Диском
    yandex_disk = YandexDiskAPI(env_vars['YANDEX_DISK_TOKEN'], env_vars['YANDEX_DISK_FOLDER'])

    # Первичная синхронизация
    # ...

    # Запуск отслеживания изменений в локальной папке
    # ...


if __name__ == "__main__":
    main()
