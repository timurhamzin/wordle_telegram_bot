import enum
import logging
from functools import wraps
from typing import Callable, Union

import aiohttp


async def fetch(session: aiohttp.ClientSession, url: str, **kwargs):
    """Get a GET request's text asychronously"""
    async with session.get(url, **kwargs) as response:
        if response.status == 200:
            encoding = response.charset or 'utf-8'
            response = await response.content.read()
            return response.decode(encoding)
        elif response.status == 302:
            location = response.headers.get('Location')
            return await fetch(session, location, **kwargs)
        else:
            response.raise_for_status()

def limit_results_to(top_n):
    """Parametrized decorator limiting returned list of a function
    to `top_n` first elements"""

    def limit_results(async_func: Callable):
        @wraps(async_func)
        async def inner(*args, **kwargs):
            result: list = await async_func(*args, **kwargs)
            return result[:top_n]

        return inner

    return limit_results


class LoggingLevel(enum.Enum):
    DEBUG = enum.auto()
    INFO = enum.auto()
    WARNING = enum.auto()
    ERROR = enum.auto()
    CRITICAL = enum.auto()


def log_at_level(logger: logging.Logger, level: LoggingLevel, msg: str):
    if level == LoggingLevel.DEBUG:
        logger.debug(msg)
    elif level == LoggingLevel.INFO:
        logger.info(msg)
    elif level == LoggingLevel.WARNING:
        logger.warning(msg)
    elif level == LoggingLevel.ERROR:
        logger.error(msg)
    elif level == LoggingLevel.CRITICAL:
        logger.critical(msg)


def raise_with_log(
        module_name_or_logger: Union[str, logging.Logger],
        exception: Exception, level: LoggingLevel = LoggingLevel.ERROR
):
    logger = (module_name_or_logger
              if isinstance(module_name_or_logger, logging.Logger)
              else logging.getLogger(module_name_or_logger))
    msg: str = f'{exception}\n{exception.__traceback__}'
    log_at_level(logger, level, msg)
    if exception.__traceback__ is not None:
        raise exception.with_traceback(exception.__traceback__)
    else:
        raise exception


def log(
        module_name_or_logger: Union[str, logging.Logger],
        msg: str, level: LoggingLevel = LoggingLevel.ERROR
):
    logger = (module_name_or_logger
              if isinstance(module_name_or_logger, logging.Logger)
              else logging.getLogger(module_name_or_logger))
    log_at_level(logger, level, msg)
