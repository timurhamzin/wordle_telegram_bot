import asyncio
import datetime
import logging
import os

import telegram
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

from poller import Poller
from worker import Worker

load_dotenv()

PRACTICUM_TOKEN: str = os.environ['PRACTICUM_TOKEN']
TELEGRAM_BOT_TOKEN: str = os.environ['TELEGRAM_BOT_TOKEN']


def get_logger() -> logging.Logger:
    import logging

    # Create logger
    result_logger = logging.getLogger(__name__)
    result_logger.setLevel(logging.DEBUG)

    # Create file handler
    file_handler = logging.FileHandler('wordle_bot_log.log')
    file_handler.setLevel(logging.DEBUG)

    # Create stdout handler
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Set formatter for handlers
    file_handler.setFormatter(formatter)
    stdout_handler.setFormatter(formatter)

    # Add handlers to logger
    result_logger.addHandler(file_handler)
    result_logger.addHandler(stdout_handler)

    return result_logger


class WordleBot:
    def __init__(self, token: str, n: int):
        self.bot: telegram.Bot = ApplicationBuilder().token(token).build().bot
        self.queue: asyncio.Queue = asyncio.Queue()
        self.producer: Poller = Poller(self.bot, self.queue)
        self.consumer: Worker = Worker(self.bot, self.queue, n)

    async def start(self):
        await self.producer.start()
        await self.consumer.start()

    async def stop(self):
        await self.producer.stop()
        await self.consumer.stop()


def run():
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    bot: WordleBot = WordleBot(TELEGRAM_BOT_TOKEN, 2)
    try:
        print('Bot has been started.')
        loop.create_task(bot.start())
        loop.run_forever()
    except KeyboardInterrupt:
        print(f'Stopping {bot.__class__.__name__}', datetime.datetime.now())
        loop.run_until_complete(bot.stop())
        print(f'{bot.__class__.__name__} has been stopped',
              datetime.datetime.now())


if __name__ == "__main__":
    logger = get_logger()
    if any(not v for v in (PRACTICUM_TOKEN, TELEGRAM_BOT_TOKEN)):
        exit_msg: str = 'Cannot start bot, check your environment variables.'
        logging.critical(exit_msg)
        raise SystemExit(exit_msg)
    run()
