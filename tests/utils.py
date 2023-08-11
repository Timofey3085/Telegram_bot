import logging
import signal
import re
from collections import namedtuple
from contextlib import contextmanager
from functools import wraps
from http import HTTPStatus
from inspect import signature
from types import ModuleType


def get_clean_source_code(raw_src: str) -> str:
    comment_pattern = re.compile(r'\s*#[^\n]*')
    return re.sub(comment_pattern, '', raw_src)


def check_function(scope: ModuleType, func_name: str, params_qty: int = 0):
    """If scope has a function with specific name and params with qty."""
    assert hasattr(scope, func_name), (
        f'Не найдена функция `{func_name}`. '
        'Не удаляйте и не переименовывайте её.'
    )

    func = getattr(scope, func_name)

    assert callable(func), (
        f'`{func_name}` должна быть функцией'
    )

    sig = signature(func)
    assert len(sig.parameters) == params_qty, (
        f'Функция `{func_name}` должна принимать '
        f'количество аргументов: {params_qty}'
    )


def check_docstring(scope: ModuleType, func_name: str):
    assert hasattr(scope, func_name), (
        f'Не найдена функция `{func_name}`. '
        'Не удаляйте и не переименовывайте её.'
    )
    assert getattr(scope, func_name).__doc__, (
        f'Убедитесь, что в функции `{func_name}` есть docstring.'
    )


def check_default_var_exists(scope: ModuleType, var_name: str) -> None:
    """
    If precode variable exists in scope with a proper type.

    :param scope: Module to look for a variable
    :param var_name: Variable you want to check
    :return: None. It's an assert
    """
    assert hasattr(scope, var_name), (
        f'Не найдена переменная `{var_name}`. '
        'Не удаляйте и не переименовывайте ее.'
    )
    var = getattr(scope, var_name)
    assert not callable(var), (
        f'`{var_name}` должна быть переменной, а не функцией.'
    )


@contextmanager
def check_logging(caplog, level, message):
    """
    Check if a log message of the specified level appears during code
    execution in the context manager.
    """
    with caplog.at_level(level):
        yield
        log_record = [
            record for record in caplog.records
            if record.levelname == logging.getLevelName(level)
        ]
        assert len(log_record) > 0, message


InvalidResponse = namedtuple('InvalidResponse', ('data', 'defected_key'))


class MockResponseGET:
    CALLED_LOG_MSG = 'Request is sent'

    def __init__(self, *args, random_timestamp=None,
                 http_status=HTTPStatus.OK, data=None, **kwargs):
        self.random_timestamp = random_timestamp
        self.status_code = http_status
        self.reason = ''
        self.text = ''
        default_data = {
            'homeworks': [],
            'current_date': self.random_timestamp
        }
        self.data = default_data if data is None else data
        logging.warn(MockResponseGET.CALLED_LOG_MSG)

    def json(self):
        return self.data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise ValueError('Server or client error.')


class MockTelegramBot:
    def __init__(self, **kwargs):
        self._is_message_sent = False

    def send_message(self, chat_id=None, text=None, **kwargs):
        self.is_message_sent = True
        self.chat_id = chat_id
        self.text = text


class BreakInfiniteLoop(Exception):
    pass


class TestTimeoutError(BaseException):
    pass


class Timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TestTimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


def with_timeout(f):
    """Make function raise TimeoutError after `timeout` seconds.
    This is a decorator.
    """
    timeout = 1

    @wraps(f)
    def inner():
        try:
            try:
                with Timeout(seconds=timeout):
                    # Run main expecting BreakInfiniteLoop
                    f()
            except TestTimeoutError:
                pass
        except BreakInfiniteLoop:
            # intercept higher up in the call hierarchy
            raise
        else:
            # homework_module.main() timed out
            raise AssertionError(
                'Убедитесь, что внутри цикла `while True` функции `main` при '
                'любом сценарии исполнения кода выполняется функция '
                '`time.sleep()`.'
            )

    return inner
