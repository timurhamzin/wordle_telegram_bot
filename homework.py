import os
import requests
import telegram
import time
from dotenv import load_dotenv
import logging

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework['status'] == 'approved':
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    else:
        verdict = 'Работе присвоен неизвестный статус.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    params = {
        'from_date': current_timestamp
    }
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    try:
        homework_statuses = requests.get(url=url, headers=headers, params=params)
        return homework_statuses.json()
    except requests.RequestException as e:
        logging.error(f'Error: {e}')


def send_message(message):
    proxy = telegram.utils.request.Request(
        proxy_url='socks5://109.194.175.135:9050')
    bot = telegram.Bot(token=TELEGRAM_TOKEN, request=proxy)
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
                current_timestamp = new_homework.get('current_date')
                if current_timestamp and isinstance(current_timestamp, int):
                    time.sleep(300)
                else:
                    raise TypeError(f'Positive integer is expected for '
                                    f'current_timestamp, got {current_timestamp}.')

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
