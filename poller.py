import asyncio
import logging

import telegram
from bunch import bunchify

from echo_bot_example import logger


class Poller:
    """Task producer, long-polling the bot for updates.
    Updates are put into the queue in the form of objects."""

    def __init__(self, bot: telegram.Bot, queue: asyncio.Queue):
        self.queue = queue
        self.bot = bot

    async def _worker(self):
        offset: int = 0
        while True:
            res = await self.bot.get_updates(offset=offset, timeout=60)
            for item in res:
                item = bunchify(item)
                offset: int = item.update_id + 1
                await self.queue.put(item)
                logging.info(f'Received a message: `{item.message.text}`')

    async def start(self):
        task_logger.create_task(
            self._worker(), logger=logger,
            message='Poller task raised an exception',
            loop=asyncio.get_event_loop())