![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=Hi,+I'am+a+Python+developer.)](https://git.io/typing-svg)

# Telegram-bot

## Телеграм-бот для отслеживания статуса проверки домашней работы на Яндекс Практикум.

### Присылает сообщения, когда статус изменен - взято в проверку, есть замечания, зачтено.

#### Технологии:
- Python 3.9
- python-dotenv 0.19.0
- python-telegram-bot 13.7

#### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:PashkaVRN/homework_bot.git
cd homework_bot
```
#### Cоздать и активировать виртуальное окружение:
```
python -m venv env
source env/bin/activate
```
#### Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
#### Записать в переменные окружения (файл .env) необходимые ключи:

- токен профиля на Яндекс.Практикуме
- токен телеграм-бота
- свой ID в телеграме

#### Запустить проект:
```
python homework.py
```

Автор
[Timofey - Razborshchikov](https://github.com/Timofey3085)
