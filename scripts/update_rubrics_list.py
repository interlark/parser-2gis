#!/usr/bin/env python3

# Download rubrics.

import json
import os
import sys

for _ in range(2):
    try:
        import parser_2gis.paths
        from parser_2gis.chrome import (ChromeOptions,
                                        ChromeRemote)
        break
    except ImportError:
        here = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.abspath(os.path.join(here, os.pardir))
        if parent_dir not in sys.path:
            sys.path.insert(1, parent_dir)

# Get available cities from https://data.2gis.com and save it to data/rubrics.json

_REGIONS_LIST_RESPONSE = r'https://hermes.2gis.ru/api/data/availableParameters'

chrome_options = ChromeOptions(headless=True)
with ChromeRemote(chrome_options, [_REGIONS_LIST_RESPONSE]) as chrome_remote:
    chrome_remote.navigate('https://data.2gis.com')
    response = chrome_remote.wait_response(_REGIONS_LIST_RESPONSE)
    doc = chrome_remote.get_response_body(response)

    if not doc:
        print('No response, bail!', file=sys.stderr)
        exit(1)

    # Cherry-pick
    rubrics = doc['rubrics']
    for v in rubrics.values():
        del v['totalCount']
        del v['GroupId']

    # Check for special None rubric
    assert any(x['label'] == 'Без рубрики' for x in rubrics.values())

    # Save rubrics list
    rubrics_path = parser_2gis.paths.data_path('rubrics.json')
    with open(rubrics_path, 'w', encoding='utf-8') as f:
        json.dump(rubrics, f, ensure_ascii=False, indent=4)
