import logging
from sys import stdout

formatter: logging.Formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s')

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler: logging.Handler = logging.StreamHandler(stream=stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)
