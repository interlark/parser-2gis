#!/usr/bin/env python3

# Download cities info for following countries:
# ae, az, bh, by, cl, cy, cz, eg, it, kg, kw, kz, om, qa, ru, sa, ua, uz

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

# Get available cities from https://data.2gis.com and save it to data/cities.json

_REGIONS_LIST_RESPONSE = r'https://catalog\.api\.2gis.[^/]+/.*/region/list'

# NOTE:
# There are also cities list in 'https://hermes.2gis.ru/api/data/availableParameters'
# It has less entries than in '/region/list', but more structured (tree vs flat list).
# Better use '/region/list' for parsing purpose.

chrome_options = ChromeOptions(headless=True)
with ChromeRemote(chrome_options, [_REGIONS_LIST_RESPONSE]) as chrome_remote:
    chrome_remote.navigate('https://data.2gis.com')
    response = chrome_remote.wait_response(_REGIONS_LIST_RESPONSE)
    data = chrome_remote.get_response_body(response)

    try:
        doc = json.loads(data)
    except json.JSONDecodeError:
        print('Returned invalid JSON document!', file=sys.stderr)
        exit(1)

    if not doc:
        print('No response, bail!', file=sys.stderr)
        exit(1)

    cities = []
    for item in doc['result']['items']:
        cities.append({
            # "name" could contain trailing underscore char
            # for some reasons, get rid of it.
            'name': item['name'].strip('_'),
            'code': item['code'],
            'domain': item['domain'],
            'country_code': item['country_code'],
        })

    cities = sorted(cities, key=lambda x: x['domain'])
    cities_path = parser_2gis.paths.data_path() / 'cities.json'
    with open(cities_path, 'w', encoding='utf-8') as f:
        json.dump(cities, f, ensure_ascii=False, indent=4)
