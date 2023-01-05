from __future__ import annotations

from ..exceptions import ChromeRuntimeException, ChromeUserAbortException
from ..logger import logger
from ..parser import get_parser
from ..writer import get_writer
from .runner import AbstractRunner


class CLIRunner(AbstractRunner):
    """CLI runner.

    Args:
        urls: 2GIS URLs with items to be collected.
        output_path: Path to the result file.
        format: `csv`, `xlsx` or `json` format.
        config: Configuration.
    """
    def start(self):
        logger.info('Парсинг запущен.')
        try:
            with get_writer(self._output_path, self._format, self._config.writer) as writer:
                for url in self._urls:
                    logger.info(f'Парсинг ссылки {url}')
                    with get_parser(url,
                                    chrome_options=self._config.chrome,
                                    parser_options=self._config.parser) as parser:
                        try:
                            parser.parse(writer)
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

    def stop(self):
        pass
