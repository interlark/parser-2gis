from __future__ import annotations

import csv
import os
import re
import shutil
from typing import Any, Callable

from pydantic import ValidationError

from ...common import report_from_validation_error
from ...logger import logger
from ..models import CatalogItem
from .file_writer import FileWriter


class CSVWriter(FileWriter):
    """Writer to CSV table."""
    @property
    def _complex_mapping(self) -> dict[str, Any]:
        # Complex mapping means its content could contain several entities bound by user settings.
        # For example: phone -> phone_1, phone_2, ..., phone_n
        return {
            'phone': 'Телефон', 'email': 'E-mail',
            'website': 'Веб-сайт', 'instagram': 'Instagram', 'twitter': 'Twitter', 'facebook': 'Facebook',
            'vkontakte': 'ВКонтакте', 'youtube': 'YouTube', 'skype': 'Skype'
        }

    @property
    def _data_mapping(self) -> dict[str, Any]:
        data_mapping = {
            'name': 'Наименование', 'description': 'Описание', 'rubrics': 'Рубрики',
            'address': 'Адрес', 'address_comment': 'Комментарий к адресу',
            'postcode': 'Почтовый индекс', 'living_area': 'Микрорайон', 'district': 'Район', 'city': 'Город',
            'district_area': 'Округ', 'region': 'Регион', 'country': 'Страна', 'schedule': 'Часы работы',
            'timezone': 'Часовой пояс',
        }

        # Expand complex mapping
        for k, v in self._complex_mapping.items():
            for n in range(1, self._options.csv.columns_per_entity + 1):
                data_mapping[f'{k}_{n}'] = f'{v} {n}'

        if not self._options.csv.add_rubrics:
            data_mapping.pop('rubrics', None)

        return {
            **data_mapping,
            **{
                'point_lat': 'Широта',
                'point_lon': 'Долгота',
                'url': '2GIS URL',
            }
        }

    def _writerow(self, row: dict[str, Any]) -> None:
        """Write a `row` into CSV."""
        if self._options.verbose:
            logger.info('Парсинг [%d] > %s', self._wrote_count + 1, row['name'])

        try:
            self._writer.writerow(row)
        except Exception as e:
            logger.error('Ошибка во время записи: %s', e)

    def __enter__(self) -> CSVWriter:
        super().__enter__()
        self._writer = csv.DictWriter(self._file, self._data_mapping.keys())
        self._writer.writerow(self._data_mapping)  # Write header
        self._wrote_count = 0
        return self

    def __exit__(self, *exc_info) -> None:
        super().__exit__(*exc_info)
        if self._options.csv.remove_empty_columns:
            logger.info('Удаление пустых колонок CSV.')
            self._remove_empty_columns()
        if self._options.csv.remove_duplicates:
            logger.info('Удаление повторяющихся записей CSV.')
            self._remove_dublicates()

    def _remove_empty_columns(self) -> None:
        """Postprocess: Remove empty columns."""
        complex_columns = self._complex_mapping.keys()
        complex_columns_count = {c: 0 for c in self._data_mapping.keys() if
                                 re.match('|'.join(fr'^{x}_\d+$' for x in complex_columns), c)}

        # Looking for empty columns
        with self._open_file(self._file_path, 'r') as f_csv:
            csv_reader = csv.DictReader(f_csv, self._data_mapping.keys())  # type: ignore
            next(csv_reader, None)  # Skip header
            for row in csv.DictReader(f_csv, self._data_mapping.keys()):  # type: ignore
                for column_name in complex_columns_count.keys():
                    if row[column_name] != '':
                        complex_columns_count[column_name] += 1

        # Generate new data mapping
        new_data_mapping: dict[str, Any] = {}
        for k, v in self._data_mapping.items():
            if k in complex_columns_count:
                if complex_columns_count[k] > 0:
                    new_data_mapping[k] = v
            else:
                new_data_mapping[k] = v

        # Rename single complex column - remove postfix numbers
        for column in complex_columns:
            if f'{column}_1' in new_data_mapping and f'{column}_2' not in new_data_mapping:
                new_data_mapping[f'{column}_1'] = re.sub(r'\s+\d+$', '', new_data_mapping[f'{column}_1'])

        # Populate new csv
        tmp_csv_name = os.path.splitext(self._file_path)[0] + '.removed-columns.csv'

        with self._open_file(tmp_csv_name, 'w') as f_tmp_csv, \
                self._open_file(self._file_path, 'r') as f_csv:
            csv_writer = csv.DictWriter(f_tmp_csv, new_data_mapping.keys())  # type: ignore
            csv_reader = csv.DictReader(f_csv, self._data_mapping.keys())  # type: ignore
            csv_writer.writerow(new_data_mapping)  # Write new header
            next(csv_reader, None)  # Skip header

            for row in csv_reader:
                new_row = {k: v for k, v in row.items() if k in new_data_mapping}
                csv_writer.writerow(new_row)

        # Replace original table with new one
        shutil.move(tmp_csv_name, self._file_path)

    def _remove_dublicates(self) -> None:
        """Postprocess: Remove dublicates."""
        tmp_csv_name = os.path.splitext(self._file_path)[0] + '.deduplicated.csv'
        with self._open_file(tmp_csv_name, 'w') as f_tmp_csv, \
                self._open_file(self._file_path, 'r') as f_csv:
            seen_records = set()
            for line in f_csv:
                if line in seen_records:
                    continue

                seen_records.add(line)
                f_tmp_csv.write(line)

        # Replace original table with new one
        shutil.move(tmp_csv_name, self._file_path)

    def write(self, catalog_doc: Any) -> None:
        """Write Catalog Item API JSON document down to CSV table.

        Args:
            catalog_doc: Catalog Item API JSON document.
        """
        if not self._check_catalog_doc(catalog_doc):
            return

        row = self._extract_raw(catalog_doc)
        if row:
            self._writerow(row)
            self._wrote_count += 1

    def _extract_raw(self, catalog_doc: Any) -> dict[str, Any]:
        """Extract data from Catalog Item API JSON document.

        Args:
            catalog_doc: Catalog Item API JSON document.

        Returns:
            Dictionary for CSV row.
        """
        data: dict[str, Any] = {k: None for k in self._data_mapping.keys()}

        item = catalog_doc['result']['items'][0]

        try:
            catalog_item = CatalogItem(**item)
        except ValidationError as e:
            errors = []
            errors_report = report_from_validation_error(e, item)
            for path, description in errors_report.items():
                arg = description['invalid_value']
                error_msg = description['error_message']
                errors.append(f'[*] Поле: {path}, значение: {arg}, ошибка: {error_msg}')

            error_str = 'Ошибка парсинга:\n' + '\n'.join(errors)
            logger.error(error_str)

            return {}

        # Name, description
        data['name'] = catalog_item.name_ex.primary
        data['description'] = catalog_item.name_ex.extension

        # Address
        data['address'] = catalog_item.address_name

        # Point location
        if catalog_item.point:
            data['point_lat'] = catalog_item.point.lat  # Latitude (широта)
            data['point_lon'] = catalog_item.point.lon  # Longitude (долгота)

        # Address comment
        data['address_comment'] = catalog_item.address_comment

        # Post code
        if catalog_item.address:
            data['postcode'] = catalog_item.address.postcode

        # Timezone
        if catalog_item.timezone is not None:
            data['timezone'] = catalog_item.timezone

        # Administrative location details
        for div in catalog_item.adm_div:
            for t in ('country', 'region', 'district_area', 'city', 'district', 'living_area'):
                if div.type == t:
                    data[t] = div.name

        # Item URL
        data['url'] = catalog_item.url

        # Contacts
        for contact_group in catalog_item.contact_groups:
            def append_contact(contact_type: str, priority_fields: list[str],
                               formatter: Callable[[str], str] | None = None) -> None:
                """Add contact to `data`.

                Args:
                    contact_type: Contact type (see `Contact` in `catalog_item.py`)
                    priority_fields: Field of contact to be added, sorted by priotity
                    formatter: Field value formatter
                """
                contacts = [x for x in contact_group.contacts if x.type == contact_type]
                for i, contact in enumerate(contacts, 1):
                    for field in priority_fields:
                        if hasattr(contact, field):
                            contact_value = getattr(contact, field)
                            break

                    # Empty contact value, bail
                    if not contact_value:
                        return

                    data_name = f'{contact_type}_{i}'
                    if data_name in data:
                        data[data_name] = formatter(contact_value) if formatter else contact_value

                        # Add comment on demand
                        if self._options.csv.add_comments and contact.comment:
                            data[data_name] += ' (%s)' % contact.comment

            # Urls
            for t in ['website', 'vkontakte', 'instagram', 'facebook', 'twitter', 'youtube']:
                append_contact(t, ['url'])

            # Values
            for t in ['email', 'skype']:
                append_contact(t, ['value'])

            # Phone (`value` sometimes has strange crap inside, so we better parse `text`.
            # If no `text` field in contact - use `value` attribute)
            append_contact('phone', ['text', 'value'],
                           formatter=lambda x: re.sub(r'^\+7', '8', re.sub(r'[^0-9+]', '', x)))

        # Schedule
        if catalog_item.schedule:
            data['schedule'] = catalog_item.schedule.to_str(self._options.csv.join_char,
                                                            self._options.csv.add_comments)

        # Rubrics
        if self._options.csv.add_rubrics:
            data['rubrics'] = self._options.csv.join_char.join(x.name for x in catalog_item.rubrics)

        return data
