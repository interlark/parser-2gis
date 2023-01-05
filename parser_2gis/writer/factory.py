from __future__ import annotations

from typing import TYPE_CHECKING

from .writers import CSVWriter, XLSXWriter, FileWriter, JSONWriter

from .exceptions import WriterUnknownFileFormat

if TYPE_CHECKING:
    from .options import WriterOptions


def get_writer(file_path: str, file_format: str, writer_options: WriterOptions) -> FileWriter:
    """Writer factory function.

    Args:
        output_path: Path to thr result file.
        format: `csv`, `xlsx` or `json` format.
        writer_options: Writer options.

    Returns:
        File Writer instance.
    """

    if file_format == 'json':
        return JSONWriter(file_path, writer_options)
    elif file_format == 'csv':
        return CSVWriter(file_path, writer_options)
    elif file_format == 'xlsx':
        return XLSXWriter(file_path, writer_options)

    raise WriterUnknownFileFormat('Неизвестный формат файла: %s', file_format)
