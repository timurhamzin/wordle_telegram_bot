import asyncio
from asyncio import Task
from typing import Optional, Tuple

import telegram
from bunch import bunchify

from utils import task_logger
from utils.common import log, LoggingLevel


class Poller:
    """Task producer, long-polling the bot for updates.
    Updates are put into the queue in the form of objects."""

    def __init__(self, bot: telegram.Bot, queue: asyncio.Queue):
        self.queue = queue
        self.bot = bot
        self._task: Optional[Task] = None

    async def _worker(self) -> None:
        offset: int = 0
        while True:
            res: Tuple[telegram.Update]
            try:
                res = await self.bot.get_updates(offset=offset, timeout=60)
            except (telegram.error.TimedOut, telegram.error.NetworkError) as e:
                step_sec: int = 30
                log(__name__, (
                    f'There was an error getting an update : {e}\n'
                    f'Sleeping for {step_sec} seconds.'
                ), LoggingLevel.WARNING)
                await asyncio.sleep(step_sec)
            except asyncio.CancelledError:
                log(__name__, (
                    'Cancelling the poller.'
                ), LoggingLevel.WARNING)
                break
            except Exception as e:
                log(__name__, (
                    (
                        f'Exception was raised polling for updates: {e}. \n'
                        f'The poller is kept alive.'
                    )
                ), LoggingLevel.ERROR)
            else:
                for item in res:
                    item_obj: telegram.Update = bunchify(item)
                    offset = item_obj.update_id + 1
                    await self.queue.put(item_obj)
                    if item_obj.message:
                        log(__name__, (
                            f'Received a message: `{item_obj.message.text}`'
                        ), LoggingLevel.WARNING)
                    else:
                        log(__name__, (
                            f'Received an empty message.`'
                        ), LoggingLevel.WARNING)


    async def start(self):
        self._task = task_logger.create_task(
            self._worker(), message='Poller raised an exception',
            loop=asyncio.get_event_loop())

    async def stop(self):
        self._task.cancel()
