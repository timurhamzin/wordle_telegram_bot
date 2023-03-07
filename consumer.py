import asyncio
from typing import List

import telegram
from bunch import unbunchify

from utils import task_logger
from utils.common import log, LoggingLevel, log_exception
from wordle.regex_dict import create_regex_dict
from wordle.wordle_async import WordleGame, WordleException


class Worker:
    """Task consumer with several workers."""

    def __init__(self, bot: telegram.Bot, queue: asyncio.Queue,
                 concurrent_workers: int):
        self.bot = bot
        self.queue = queue
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []

    async def handle_update(self, update: telegram.Update) -> None:
        log(__name__, f'Got update {unbunchify(update)}', LoggingLevel.INFO)
        my_game = WordleGame(
            regex_dict=create_regex_dict(timeout_secs=10), word_length=5
        )
        attempts: List[str] = update.message.text.split()
        try:
            response = await my_game.play(attempts)
        except WordleException as e:
            await self.bot.send_message(update.message.chat_id,
                                        f'{e}\n\n{WordleGame.rules}')
        else:
            try:
                await self.bot.send_message(update.message.chat_id, response)
            except Exception as e:
                log_exception(__name__, e, reraise=False)

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
                    self._worker(),
                    message='Worker task raised an exception',
                    loop=asyncio.get_event_loop())
            )

    async def stop(self):
        await self.queue.join()
        for t in self._tasks:
            t.cancel()
