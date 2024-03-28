from typing import Dict, Any
from dotenv import dotenv_values


def read_env() -> Dict[str, Any]:
    """
    Функция получения параметров окружения
    :return: Словарь с переменными окружения и их значениями
    """
    return dotenv_values(".env")
