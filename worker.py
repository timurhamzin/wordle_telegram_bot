import asyncio

import telegram
from bunch import unbunchify

from echo_bot_example import logger


class Worker:
    """Task consumer with several workers."""

    def __init__(self, bot: telegram.Bot, queue: asyncio.Queue,
                 concurrent_workers: int):
        self.bot = bot
        self.queue = queue
        self.concurrent_workers = concurrent_workers

    @staticmethod
    async def handle_update(update):
        print("about to consume an updated")
        await asyncio.sleep(2)
        print(f'Handled item {unbunchify(update)}')

    async def _worker(self):
        while True:
            upd = await self.queue.get()
            await self.handle_update(upd)

    async def start(self):
        for _ in range(self.concurrent_workers):
            task_logger.create_task(
                self._worker(), logger=logger,
                message='Worker task raised an exception',
                loop=asyncio.get_event_loop())