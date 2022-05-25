from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import ChromeRuntimeException, ChromeUserAbortException
from ..logger import logger, setup_cli_logger
from ..parser import Parser2GIS
from ..writer import get_writer

if TYPE_CHECKING:
    from ..config import Configuration


def run_cli(urls: str, output_path: str, format: str, config: Configuration) -> None:
    """Run CLI Parser

    Args:
        urls: 2GIS URLs with result items to be collected.
        output_path: Path to the result file.
        format: `csv` or `json`.
        config: Configuration.
    """
    setup_cli_logger(config.log)

    logger.info('Парсинг запущен.')
    try:
        with get_writer(output_path, format, config.writer) as writer:
            for url in urls:
                logger.info(f'Парсинг ссылки {url}')
                with Parser2GIS(chrome_options=config.chrome,
                                parser_options=config.parser) as parser:
                    try:
                        parser.parse_url(url, writer)
                    finally:
                        logger.info('Парсинг ссылки завершён.')
    except (KeyboardInterrupt, ChromeUserAbortException):
        logger.error('Работа парсера прервана пользователем.')
    except Exception as e:
        if isinstance(e, ChromeRuntimeException) and str(e) == 'Tab has been stopped':
            logger.error('Вкладка браузера была закрыта.')
        else:
            logger.error('Ошибка во время работы парсера.', exc_info=True)
    finally:
        logger.info('Парсинг завершён.')
