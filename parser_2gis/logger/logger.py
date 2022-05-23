from __future__ import annotations

import logging
import os
import warnings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .options import LogOptions
    import queue


# Set third-party loggers level to error
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('pychrome').setLevel(logging.FATAL)
warnings.filterwarnings(
    action='ignore',
    module='pychrome'
)

_LOGGER_NAME = 'parser-2gis'


class QueueHandler(logging.Handler):
    def __init__(self, log_queue: queue.Queue[tuple[str, str]]) -> None:
        super().__init__()
        self._log_queue = log_queue

    def emit(self, record: logging.LogRecord) -> None:
        log_message = (record.levelname, self.format(record) + os.linesep)
        self._log_queue.put(log_message)


def setup_gui_logger(log_queue: queue.Queue[tuple[str, str]],
                     options: LogOptions) -> None:
    """Add queue handler to existing logger so it would
    emmit logs to the specified queue.

    Args:
        log_queue: Queue to put logging messages into.
    """
    formatter = logging.Formatter(options.gui_format, options.gui_datefmt)
    queue_handler = QueueHandler(log_queue)
    queue_handler.setFormatter(formatter)
    logger.addHandler(queue_handler)


def setup_cli_logger(options: LogOptions) -> None:
    """Setup CLI logger from config.

    Args:
        options: Log options.
    """
    setup_logger(
        options.level,
        options.cli_format,
        options.cli_datefmt,
    )


def setup_logger(level: str, fmt: str, datefmt: str) -> None:
    """Setup logger.

    Args:
        level: logger level.
        fmt: format string in percent style.
        datefmt: date format string.
    """
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt, datefmt)
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(level)


logger = logging.getLogger(_LOGGER_NAME)
