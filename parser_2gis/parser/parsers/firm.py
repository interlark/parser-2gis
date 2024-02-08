from __future__ import annotations

from typing import TYPE_CHECKING

from ...logger import logger
from .main import MainParser

if TYPE_CHECKING:
    from ...writer import FileWriter


class FirmParser(MainParser):
    """Parser for the firms provided by 2GIS.

    URL pattern for such cases: https://2gis.<domain>/<city_id>/firm/<firm_id>
    """
    @staticmethod
    def url_pattern():
        """URL pattern for the parser."""
        return r'https?://2gis\.[^/]+(/[^/]+)?/firm/.*'

    def parse(self, writer: FileWriter) -> None:
        """Parse URL with an organization.

        Args:
            writer: Target file writer.
        """
        # Go URL
        self._chrome_remote.navigate(self._url, referer='https://google.com', timeout=120)

        # Document loaded, get its response
        responses = self._chrome_remote.get_responses(timeout=5)
        if not responses:
            logger.error('Ошибка получения ответа сервера.')
            return
        document_response = responses[0]

        # Handle 404
        assert document_response['mimeType'] == 'text/html'
        if document_response['status'] == 404:
            logger.warn('Сервер вернул сообщение "Организация не найдена".')

            if self._options.skip_404_response:
                return

        # Wait all 2GIS requests get finished
        self._wait_requests_finished()

        # Gather response and collect useful payload.
        initial_state = self._chrome_remote.execute_script('window.initialState')
        data = list(initial_state['data']['entity']['profile'].values())
        if not data:
            logger.warn('Данные организации не найдены.')
            return
        doc = data[0]

        # Write API document into a file
        writer.write({
            'result': {
                'items': [doc['data']]
            },
            'meta': doc['meta']
        })
