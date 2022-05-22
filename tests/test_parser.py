import csv
import json
import os
import sys
from tempfile import TemporaryDirectory

import pytest
from parser_2gis import main as parser_main


def check_csv_result(result_path, num_records):
    """Check CSV output.

    Args:
        file_path: Path to CSV table.
        num_records: Expected number of records.
    """
    with open(result_path, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.reader(f)
        assert len(list(reader)) == num_records + 1  # `num_records` + header


def check_json_result(result_path, num_records):
    """Check JSON output.

    Args:
        file_path: Path to JSON file.
        num_records: Expected number of records.
    """
    with open(result_path, 'r', encoding='utf-8-sig', errors='replace') as f:
        doc = json.load(f)
        assert len(doc) == num_records


testdata = [
    ['csv', check_csv_result],
    ['json', check_json_result],
]


@pytest.mark.parametrize('format, result_checker', testdata)
def test_parser(monkeypatch, format, result_checker, num_records=5):
    """Parse TOP `num_records` entries and check result file.

    Args:
        format: Result format (`csv` or `json`).
        result_checker: Function that checks parsed result.
        num_records: Number of records to be parsed.
    """
    with monkeypatch.context() as m, TemporaryDirectory() as tmpdir:
        result_path = os.path.join(tmpdir, f'output.{format}')

        m.setattr(sys, 'argv', [
            os.path.abspath(__file__),
            '-i', 'https://2gis.ru/moscow/search/Аптеки',
            '-o', result_path,
            '-f', format,
            '--parser.max-records', f'{num_records}',
            '--chrome.headless', 'yes',
        ])

        # Run parser on a popular query
        # that gotta have at least `num_records` records.
        parser_main()

        # Check parsed results
        result_checker(result_path, num_records)
