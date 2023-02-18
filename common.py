import logging
from sys import stdout


def create_root_logger() -> logging.Logger:
    import logging

    # Create logger
    result_logger = logging.getLogger()
    result_logger.setLevel(logging.DEBUG)

    # Create file handler
    file_handler = logging.FileHandler('wordle_bot_log.log')
    file_handler.setLevel(logging.DEBUG)

    # Create stdout handler
    stdout_handler = logging.StreamHandler(stream=stdout)
    stdout_handler.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Set formatter for handlers
    file_handler.setFormatter(formatter)
    stdout_handler.setFormatter(formatter)

    # Add handlers to logger
    result_logger.addHandler(file_handler)
    result_logger.addHandler(stdout_handler)

    return result_logger
