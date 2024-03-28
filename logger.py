from loguru import logger


def setup_logger(log_file: str) -> None:
    """
    Функция настройки логгера
    :param log_file: Путь к файлу лога
    :return: None
    """
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}",
        level="INFO",
    )
