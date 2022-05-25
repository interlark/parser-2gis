from __future__ import annotations

import json
import os
from typing import Any

from ...logger import logger
from .file_writer import FileWriter


class JSONWriter(FileWriter):
    """Writer to JSON file."""
    def __enter__(self) -> JSONWriter:
        super().__enter__()
        self._wrote_count = 0
        self._file.write('[')
        return self

    def __exit__(self, *exc_info) -> None:
        if self._wrote_count > 0:
            self._file.write(os.linesep)
        self._file.write(']')
        super().__exit__(*exc_info)

    def _writedoc(self, catalog_doc: Any) -> None:
        """Write a `catalog_doc` into JSON document."""
        if self._options.verbose:
            item = catalog_doc['result']['items'][0]
            try:
                name = item['name_ex']['primary']
            except KeyError:
                name = '...'

            logger.info('Парсинг [%d] > %s', self._wrote_count + 1, name)

        if self._wrote_count > 0:
            self._file.write(',')

        self._file.write(os.linesep)
        self._file.write(json.dumps(item, ensure_ascii=False))
        self._wrote_count += 1

    def write(self, catalog_doc: Any) -> None:
        """Write Catalog Item API JSON document down to JSON file.

        Args:
            catalog_doc: Catalog Item API JSON document.
        """
        if not self._check_catalog_doc(catalog_doc):
            return

        self._writedoc(catalog_doc)
