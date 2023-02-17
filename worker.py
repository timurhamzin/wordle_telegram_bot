import asyncio
import logging
from typing import List

import telegram
from bunch import unbunchify

import task_logger
from common import logger
from utils import log, LoggingLevel


class Worker:
    """Task consumer with several workers."""

    def __init__(self, bot: telegram.Bot, queue: asyncio.Queue,
                 concurrent_workers: int):
        self.bot = bot
        self.queue = queue
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []

    @staticmethod
    async def handle_update(update):
        print("about to consume an update")
        await asyncio.sleep(2)
        print(f'Handled item {unbunchify(update)}')

    async def _worker(self):
        while True:
            try:
                upd = await self.queue.get()
                await self.handle_update(upd)
            except asyncio.CancelledError:
                log(__name__, (
                    f'Cancelling a consumer worker.'
                ), LoggingLevel.WARNING)
                break
            except Exception as e:
                log(__name__, (
                    f'Exception was raised handling an update: {e}.\n'
                    f'The worker is kept alive.'
                ), LoggingLevel.ERROR)
            finally:
                self.queue.task_done()

    async def start(self):
        for _ in range(self.concurrent_workers):
            self._tasks.append(
                task_logger.create_task(
                    self._worker(), logger=logger,
                    message='Worker task raised an exception',
                    loop=asyncio.get_event_loop())
            )

    async def stop(self):
        await self.queue.join()
        for t in self._tasks:
            t.cancel()
