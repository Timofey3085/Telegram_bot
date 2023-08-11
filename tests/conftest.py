import os
import sys

import pytest_timeout

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir_content = os.listdir(BASE_DIR)
HOMEWORK_FILENAME = 'homework.py'
# проверяем, что в корне репозитория лежит файл с домашкой
if (
    HOMEWORK_FILENAME not in root_dir_content or os.path.isdir(
        os.path.join(BASE_DIR, HOMEWORK_FILENAME))
):
    assert False, (
        f'В директории `{BASE_DIR}` не найден файл '
        f'с домашней работой `{HOMEWORK_FILENAME}`. '
    )

pytest_plugins = [
    'tests.fixtures.fixture_data'
]

TIMEOUT_ASSERT_MSG = (
    'Проект работает некорректно, проверка прервана.\n'
    'Вероятные причины ошибки:\n'
    '1. Исполняемый код (например, вызов функции `main()`) оказался в '
    'глобальной зоне видимости. Как исправить: закройте исполняемый код '
    'конструкцией `if __name__ == "__main__":`\n'
    '2. Инструкция `time.sleep()` в цикле `while True` в функции `main()` при '
    'каких-то условиях не выполняется. Как исправить: измените код так, чтобы '
    'эта инструкция выполнялась при любом сценарии выполнения кода.'
)


def write_timeout_reasons(text, stream=None):
    """Write possible reasons of tests timeout to stream.

    The function to replace pytest_timeout traceback output with possible
    reasons of tests timeout.
    Appears only when `thread` method is used.
    """
    if stream is None:
        stream = sys.stderr
    text = TIMEOUT_ASSERT_MSG
    stream.write(text)


pytest_timeout.write = write_timeout_reasons

os.environ['PRACTICUM_TOKEN'] = 'sometoken'
os.environ['TELEGRAM_TOKEN'] = '1234:abcdefg'
os.environ['TELEGRAM_CHAT_ID'] = '12345'
