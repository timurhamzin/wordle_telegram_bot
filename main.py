import asyncio
import datetime
import logging
import os

import telegram
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

from common import create_root_logger
from poller import Poller
from worker import Worker

load_dotenv()

PRACTICUM_TOKEN: str = os.environ['PRACTICUM_TOKEN']
TELEGRAM_BOT_TOKEN: str = os.environ['TELEGRAM_BOT_TOKEN']


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


def run() -> None:
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
    create_root_logger()
    if any(not v for v in (PRACTICUM_TOKEN, TELEGRAM_BOT_TOKEN)):
        exit_msg: str = 'Cannot start bot, check your environment variables.'
        logging.critical(exit_msg)
        raise SystemExit(exit_msg)
    run()
