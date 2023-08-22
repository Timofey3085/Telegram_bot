from http import HTTPStatus
import logging
import os
import time
import sys

import telegram
import requests
from dotenv import load_dotenv
import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляет сообщение в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено в Telegram')
    except telegram.TelegramError:
        logging.error('Не удалось отправить сообщение в Telegram')


def get_api_answer(timestamp):
    """Делает запрос эндпоинту API-сервиса."""
    logging.debug('Отправляем запрос к эндпоинту API-сервиса')
    params = {'from_date': timestamp}
    request_params = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': params
    }
    try:
        response = requests.get(**request_params)
        if response.status_code != HTTPStatus.OK:
            raise exceptions.EndpointError(
                'Ошибка в запросе {response.status_code} с параметрами: '
                '{url}, {headers}, {params}'
                .format(**request_params))
        return response.json()

    except Exception:
        raise exceptions.EndpointError(
            f'Эндпоинт {ENDPOINT} недоступен.'
            f'Код ответа API: {response.status_code}'
        )


def check_response(response):
    """Проверяет ответ API на соответствие документации из урока API."""
    if not isinstance(response, dict):
        raise TypeError('структура данных не соответствует ожиданиям')
    if 'homeworks' not in response:
        raise KeyError('в ответе API нет ключа homeworks')
    if not isinstance(response['homeworks'], list):
        raise TypeError('homeworks не список')
    return response['homeworks']


def parse_status(homework):
    """Извлекает статус проверенной работы."""
    if not isinstance(homework, dict):
        raise TypeError('homework не словарь')
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if 'homework_name' not in homework:
        raise KeyError('В ответе нет ключа homework_name')
    if not status:
        raise KeyError('В ответе нет ключа status')
    if status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неизвестный статус работы - {status}')
    verdict = HOMEWORK_VERDICTS[homework.get('status')]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        filename='main.log',
        level=logging.DEBUG,
        encoding='utf-8',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if not check_tokens():
        logging.critical('Отсутствует обязательная переменная окружения')
        sys.exit('Программа принудительно остановлена.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    current_report = {}
    prev_report = {}
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            message = parse_status(homeworks[0])
            if message != current_report:
                send_message(bot, message)
                current_report = message
            else:
                logging.debug('Отсутсвует изменение статуса')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if current_report != prev_report:
                send_message(bot, message)
                prev_report = current_report.copy()
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
