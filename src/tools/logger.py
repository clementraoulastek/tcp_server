"""Logger module"""

import logging
import os


def setup_logger(logger_name: str) -> None:
    """
    Setup the logger

    Args:
        logger_name (str): name of the logger
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )
    # Update the log file
    file_handler = logging.FileHandler(os.path.join(os.getcwd(), logger_name))
    _set_formatter(file_handler, formatter, logger)
    # Update the console
    console_handler = logging.StreamHandler()
    _set_formatter(console_handler, formatter, logger)


def _set_formatter(
    handler: logging.Handler, formatter: logging.Formatter, logger: logging.Logger
) -> None:
    """
    Set the formatter of a handler

    Args:
        handler (logging.Handler): the handler
        formatter (logging.Formatter): the formatter
        logger (logging.Logger): the logger
    """
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
