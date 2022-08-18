from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

from ...common import wait_until_finished
from ...logger import logger
from .main import MainParser

if TYPE_CHECKING:
    from ...chrome.dom import DOMNode
    from ...writer import FileWriter


class InBuildingParser(MainParser):
    """Parser for the list of organisations provided by 2GIS with the tab "In building".

    URL pattern for such cases: https://2gis.<domain>/<city_id>/inside/<building_id>
    """

    @staticmethod
    def url_pattern():
        """URL pattern for the parser."""
        return r'https?://2gis\.[^/]+/[^/]+/inside/.*'

    @wait_until_finished(timeout=5, throw_exception=False)
    def _get_links(self) -> list[DOMNode]:
        """Extracts specific DOM node links from current DOM snapshot."""
        def valid_link(node: DOMNode) -> bool:
            if node.local_name == 'a' and 'href' in node.attributes:
                link_match = re.match(r'.+/firm/[^/]+$', node.attributes['href'])
                return bool(link_match)

            return False

        dom_tree = self._chrome_remote.get_document()
        return dom_tree.search(valid_link)

    def parse(self, writer: FileWriter) -> None:
        """Parse URL with organizations.

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
            logger.warn('Сервер вернул сообщение "Точных совпадений нет / Не найдено".')

            if self._options.skip_404_response:
                return

        # Parsed records
        collected_records = 0

        # Already visited links
        visited_links: set[str] = set()

        # Get new links
        @wait_until_finished(timeout=5, throw_exception=False)
        def get_unique_links() -> list[DOMNode]:
            links = self._get_links()
            link_addresses = set(x.attributes['href'] for x in links) - visited_links
            visited_links.update(link_addresses)
            return [x for x in links if x.attributes['href'] in link_addresses]

        # Loop down through lazy load organizations list
        while True:
            # Wait all 2GIS requests get finished
            self._wait_requests_finished()

            # Gather links to be clicked
            links = get_unique_links()
            if not links:
                break

            # Iterate through gathered links
            for link in links:
                for _ in range(3):  # 3 attempts to get response
                    # Click the link to provoke request
                    # with a auth key and secret arguments
                    self._chrome_remote.perform_click(link)

                    # Delay between clicks, could be usefull if
                    # 2GIS's anti-bot service become more strict.
                    if self._options.delay_between_clicks:
                        self._chrome_remote.wait(self._options.delay_between_clicks / 1000)

                    # Gather response and collect useful payload.
                    resp = self._chrome_remote.wait_response(self._item_response_pattern)

                    # If request is failed - repeat, otherwise go further.
                    if resp and resp['status'] >= 0:
                        break

                # Get response body data
                if resp and resp['status'] >= 0:
                    data = self._chrome_remote.get_response_body(resp, timeout=10) if resp else None

                    try:
                        doc = json.loads(data)
                    except json.JSONDecodeError:
                        logger.error('Сервер вернул некорректный JSON документ: "%s", пропуск позиции.', data)
                        doc = None
                else:
                    doc = None

                if doc:
                    # Write API document into a file
                    writer.write(doc)
                    collected_records += 1
                else:
                    logger.error('Данные не получены, пропуск позиции.')

                # We've reached our limit, bail
                if collected_records >= self._options.max_records:
                    logger.info('Спарсено максимально разрешенное количество записей с данного URL.')
                    return
