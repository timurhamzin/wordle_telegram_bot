import asyncio
import logging
import os
from sys import stdout

import telegram
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

from poller import Poller
from worker import Worker

load_dotenv()

formatter: logging.Formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s')

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler: logging.Handler = logging.StreamHandler(stream=stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

PRACTICUM_TOKEN: str = os.environ['PRACTICUM_TOKEN']
TELEGRAM_BOT_TOKEN: str = os.environ['TELEGRAM_BOT_TOKEN']

# import asyncio
#
# from bot.poller import Poller
# from bot.worker import Worker
#
#
# class Bot:
#     def __init__(self, token: str, n: int):
#         self.queue = asyncio.Queue()
#         self.poller = Poller(token, self.queue)
#         self.worker = Worker(token, self.queue, n)
#
#     async def start(self):
#         await self.poller.start()
#         await self.worker.start()


async def start_queue(bot: telegram.Bot):
    """Set up a producer, polling the bot for updates."""
    queue: asyncio.Queue = asyncio.Queue()
    producer: Poller = Poller(bot, queue)
    await producer.start()
    consumer = Worker(bot, queue, 2)
    await consumer.start()


def main(bot: telegram.Bot):
    """Runs the bot asynchronously."""
    loop = asyncio.get_event_loop()
    try:
        logger.info('Bot has been started.')
        loop.create_task(start_queue(bot))
        loop.run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    if any(not v for v in (PRACTICUM_TOKEN, TELEGRAM_BOT_TOKEN)):
        exit_msg: str = 'Cannot start bot, check your environment variables.'
        logging.critical(exit_msg)
        raise SystemExit(exit_msg)
    main(
        bot=ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build().bot
    )
