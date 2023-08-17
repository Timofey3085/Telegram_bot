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
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

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
    virable_list = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    try:
        for virable in virable_list:
            all(virable)
    except Exception as error:
        logging.critical(
            f'Одной из переменных окружения не существует: {error}')
        sys.exit()


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
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
        if response.status_code != HTTPStatus.OK:
            raise exceptions.EndpointError(
                'Неверные значения токена/времени в запросе.'
                f'Код ответа API: {response.status_code}'
            )
        return response.json()

    except Exception:
        raise exceptions.EndpointError(
            f'Эндпоинт {ENDPOINT} недоступен.'
            f'Код ответа API: {response.status_code}'
        )


def check_response(response):
    """Проверяет ответ API на соответствие документации из урока API."""
    if ('homeworks' not in response or not
            isinstance(response['homeworks'], list) or not
            isinstance(response, dict)):
        error_message = 'Неверный формат данных в ответе API'
        logging.error(error_message)
        raise TypeError(error_message)
    return response['homeworks']


def parse_status(homework):
    """Извлекает статус проверенной работы."""
    try:
        status = homework['status']
        homework_name = homework['homework_name']
        verdict = HOMEWORK_VERDICTS[status]
    except KeyError:
        raise KeyError('Не хватает ключа')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        filename='main.log',
        level=logging.INFO,
        encoding='utf-8',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    while True:
        timestamp = int(time.time())
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            if len(response.get('homeworks')) != 0:
                message = parse_status(response['homeworks'][0])
                send_message(bot, message)
            else:
                logging.debug('Работа пока не проверена')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
