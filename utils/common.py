import enum
import logging
from sys import stdout
from typing import Union, Optional

import aiohttp


async def fetch(session: aiohttp.ClientSession, url: str, **kwargs
                ) -> Optional[str]:
    """Get a GET request's text asychronously"""
    async with session.get(url, **kwargs) as response:
        if response.status == 200:
            encoding: str = response.charset or 'utf-8'
            content: bytes = await response.content.read()
            return content.decode(encoding)
        elif response.status == 302:
            location = response.headers.get('Location')
            assert isinstance(location, str)
            return await fetch(session, location, **kwargs)
        else:
            response.raise_for_status()
            return None


async def post(session: aiohttp.ClientSession, url: str, data: dict, **kwargs):
    """Get a POST request's text asychronously"""
    async with session.post(url, data=data, **kwargs) as response:
        return await response.text()


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


def log_exception(
        module_name_or_logger: Union[str, logging.Logger],
        exception: Exception, level: LoggingLevel = LoggingLevel.ERROR,
        reraise=True
) -> None:
    logger = (module_name_or_logger
              if isinstance(module_name_or_logger, logging.Logger)
              else logging.getLogger(module_name_or_logger))
    msg: str = f'{exception}\n{exception.__traceback__}'
    log_at_level(logger, level, msg)
    if exception.__traceback__ is not None:
        if reraise:
            raise exception.with_traceback(exception.__traceback__)
    else:
        raise exception
    return None


def log(
        module_name_or_logger: Union[str, logging.Logger],
        msg: str, level: LoggingLevel = LoggingLevel.ERROR
) -> None:
    logger = (module_name_or_logger
              if isinstance(module_name_or_logger, logging.Logger)
              else logging.getLogger(module_name_or_logger))
    log_at_level(logger, level, msg)
    return None


def create_root_logger() -> logging.Logger:
    import logging

    result_logger = logging.getLogger()
    result_logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler('wordle_bot_log.log')
    file_handler.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler(stream=stdout)
    stdout_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler.setFormatter(formatter)
    stdout_handler.setFormatter(formatter)

    result_logger.addHandler(file_handler)
    result_logger.addHandler(stdout_handler)

    return result_logger