import asyncio
import logging
import os
import time
from sys import stdout
from typing import Optional

import telegram
from dotenv import load_dotenv
from telegram.ext import CommandHandler, ApplicationBuilder

from bot_handlers import start, send_message

from parse_response import (
    parse_homework_status, get_homework_statuses, get_current_timestamp)

load_dotenv()

formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

PRACTICUM_TOKEN: str = os.environ['PRACTICUM_TOKEN']
TELEGRAM_BOT_TOKEN: str = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID: str = ''
BOT: Optional[telegram.Bot] = None
PROXY: Optional[str] = os.getenv('TELEGRAM_PROXY')
SLEEP_SECS_ON_SUCCESS: int = 300
SLEEP_SECS_ON_ERROR: int = 60
API_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def check_started() -> None:
    if not BOT or not CHAT_ID:
        msg: str = 'Start the bot to start receiving messages.'
        logging.warning(msg)
        raise RuntimeError(msg)


async def main() -> None:
    last_status: str = ''
    current_timestamp: int = int(time.time())

    while True:
        try:
            check_started()
            new_statuses: dict = get_homework_statuses(current_timestamp)
            last_homework: dict = new_statuses['homeworks'][0]
            current_timestamp = get_current_timestamp(new_statuses)
            current_status = parse_homework_status(last_homework)
            if not last_status:
                last_status = current_status
            elif current_status != last_status:
                last_status = current_status
                await send_message(current_status)

            time.sleep(SLEEP_SECS_ON_SUCCESS)  # sleep 5 minutes
        except Exception as e:
            print(f'There was an error, check logs for details: {e}')
            time.sleep(SLEEP_SECS_ON_ERROR)
            continue


if __name__ == '__main__':
    if any(not v for v in (PRACTICUM_TOKEN, TELEGRAM_BOT_TOKEN)):
        exit_msg: str = 'Cannot start bot, check your environment variables.'
        logging.critical(exit_msg)
        raise SystemExit(exit_msg)

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    asyncio.gather(application.run_polling(), main())
