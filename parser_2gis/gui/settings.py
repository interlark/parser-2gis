from __future__ import annotations

import pydantic

from ..common import (GUI_ENABLED, report_from_validation_error,
                      running_linux, unwrap_dot_dict)
from ..config import Configuration
from ..logger import logger
from .error_popup import gui_error_popup
from .utils import ensure_gui_enabled

if GUI_ENABLED:
    import PySimpleGUI as sg


@ensure_gui_enabled
def gui_settings(config: Configuration) -> None:
    """Run settings.

    Args:
        config: Configuration to be changed.
    """
    # Window layout
    layout = [
        [
            sg.Frame('Браузер', expand_x=True, pad=((5, 5), (5, 10)), layout=[
                [
                    sg.Checkbox('Отключить изображения', pad=((0, 10), (5, 0)), key='-CHROME.DISABLE_IMAGES-',
                                tooltip='Отключить изображения для увеличения скорости работы',
                                default=config.chrome.disable_images,
                                checkbox_color=sg.theme_input_background_color(), enable_events=True),
                ],
                [
                    sg.Checkbox('Запускать развёрнутым', pad=((0, 10), (0, 0)), key='-CHROME.START_MAXIMIZED-',
                                tooltip='Запускать браузер развёрнутым во весь экран',
                                default=config.chrome.start_maximized,
                                checkbox_color=sg.theme_input_background_color(), enable_events=True),
                ],
                [
                    sg.Checkbox('Скрытый режим', pad=((0, 10), (0, 0)), key='-CHROME.HEADLESS-',
                                tooltip='Запускать браузер в скрытом виде',
                                default=config.chrome.headless,
                                checkbox_color=sg.theme_input_background_color(), enable_events=True),
                ],
                [
                    sg.Column([
                        [
                            sg.Column([
                                [
                                    sg.Text('Лимит RAM'),
                                ],
                            ], expand_x=True, pad=0),
                            sg.Column([
                                [
                                    sg.Spin([x for x in range(1, 100)], size=(6, 1), key='-CHROME.MEMORY_LIMIT-',
                                            initial_value=config.chrome.memory_limit,
                                            tooltip=('Лимит оперативной памяти браузера (мегабайт)')),
                                ],
                            ], element_justification='right', pad=0),
                        ],
                    ], expand_x=True, pad=((3, 3), (3, 5))),
                ],
            ]),
        ],
        [
            sg.Frame('Парсер', expand_x=True, pad=((5, 5), (5, 10)), layout=[
                [
                    sg.Checkbox('Показывать города', pad=((0, 10), (5, 0)), key='-WRITER.VERBOSE-',
                                tooltip='Показывать города с логе',
                                default=config.writer.verbose,
                                checkbox_color=sg.theme_input_background_color(), enable_events=True),
                ],
                # [
                #     sg.Checkbox('Сборщик мусора', pad=((0, 10), (0, 0)), key='-PARSER.USE_GC-',
                #                 tooltip='Сборщик мусора - сдерживает быстрое заполнение RAM, уменьшает скорость парсинга.',
                #                 default=config.parser.use_gc,
                #                 checkbox_color=sg.theme_input_background_color(), enable_events=True),
                # ],
                [
                    sg.Checkbox('Точные совпадения', pad=((0, 10), (0, 0)), key='-PARSER.SKIP_404_RESPONSE-',
                                tooltip='Пропускать ссылки вернувшие сообщение "Точных совпадений нет / Не найдено"',
                                default=config.parser.skip_404_response,
                                checkbox_color=sg.theme_input_background_color(), enable_events=True),
                ],
                [
                    sg.Column([
                        [
                            sg.Column([
                                [
                                    sg.Text('Задержка кликов'),
                                ],
                            ], expand_x=True, pad=0),
                            sg.Column([
                                [
                                    sg.Spin([x for x in range(1, 100000)], size=(5, 1), key='-PARSER.DELAY_BETWEEN_CLICKS-',
                                            initial_value=config.parser.delay_between_clicks,
                                            tooltip='Задержка между кликами по записям (миллисекунд)'),
                                ],
                            ], element_justification='right', pad=0),
                        ],
                    ], expand_x=True, pad=((3, 3), (3, 0))),
                ],
                [
                    sg.Column([
                        [
                            sg.Column([
                                [
                                    sg.Text('Лимит записей'),
                                ],
                            ], expand_x=True, pad=0),
                            sg.Column([
                                [
                                    sg.Spin([x for x in range(1, 100000)], size=(5, 1), key='-PARSER.MAX_RECORDS-',
                                            initial_value=config.parser.max_records,
                                            tooltip='Максимальное количество спарсенных записей с одного URL'),
                                ],
                            ], element_justification='right', pad=0),
                        ],
                    ], expand_x=True, pad=((3, 3), (3, 5))),
                ],
            ]),
        ],
        [
            sg.Frame('CSV', expand_x=True, pad=((5, 5), (5, 10)), layout=[
                [
                    sg.Checkbox('Добавить "Рубрики"', pad=((0, 10), (5, 0)), key='-WRITER.CSV.ADD_RUBRICS-',
                                tooltip='Добавить колонку "Рубрики"',
                                default=config.writer.csv.add_rubrics,
                                checkbox_color=sg.theme_input_background_color(), enable_events=True),
                ],
                [
                    sg.Checkbox('Добавлять комментарии', pad=((0, 10), (0, 0)), key='-WRITER.CSV.ADD_COMMENTS-',
                                tooltip='Добавлять комментарии к ячейкам Телефон, E-Mail, и т.д.',
                                default=config.writer.csv.add_comments,
                                checkbox_color=sg.theme_input_background_color(), enable_events=True),
                ],
                [
                    sg.Checkbox('Удалить пустые колонки', pad=((0, 10), (0, 0)), key='-WRITER.CSV.REMOVE_EMPTY_COLUMNS-',
                                tooltip='Удалить пустые колонки по завершению работы парсера',
                                default=config.writer.csv.remove_empty_columns,
                                checkbox_color=sg.theme_input_background_color(), enable_events=True),
                ],
                [
                    sg.Checkbox('Удалить дубликаты', pad=((0, 10), (0, 0)), key='-WRITER.CSV.REMOVE_DUPLICATES-',
                                tooltip='Удалить повторяющиеся записи по завершению работы парсера',
                                default=config.writer.csv.remove_duplicates,
                                checkbox_color=sg.theme_input_background_color(), enable_events=True),
                ],
                [
                    sg.Column([
                        [
                            sg.Column([
                                [
                                    sg.Text('Сложные колонки'),
                                ],
                            ], expand_x=True, pad=0),
                            sg.Column([
                                [
                                    sg.Spin([x for x in range(1, 100)], size=(5, 1), key='-WRITER.CSV.COLUMNS_PER_ENTITY-',
                                            initial_value=config.writer.csv.columns_per_entity,
                                            tooltip=('Количество колонок для результата с несколькими возможными значениями: '
                                            'Телефон_1, Телефон_2, и т.д.')),
                                ],
                            ], element_justification='right', pad=0),
                        ],
                    ], expand_x=True, pad=((3, 3), (3, 5))),
                ],
            ]),
        ],
        [
            sg.Button('Сохранить', size=(11, 1), pad=((4, 0), (7, 7)), key='-BTN_SAVE-'),
            sg.Column([
                [
                    sg.Button('Отмена', size=(8, 1), pad=((7, 0), (7, 7)),
                              key='-BTN_CANCEL-'),
                ],
            ], expand_x=True, element_justification='right'),
        ],
    ]

    window_title = 'Settings' if running_linux() else 'Настройки'
    window = sg.Window(window_title, layout, auto_size_text=True, finalize=True,
                       font='Any 12', modal=True, keep_on_top=True)

    # Main loop
    while True:
        event, values = window.Read()

        # Close window
        if event in (None, '-BTN_CANCEL-'):
            break

        # Chrome settings
        elif event == '-BTN_SAVE-':
            new_parameters_flat = {k.strip('-').lower(): v for k, v in values.items()}
            new_parameters = unwrap_dot_dict(new_parameters_flat)

            try:
                new_configuration = Configuration(**new_parameters)
                config.merge_with(new_configuration)
                config.save_config()
                break
            except pydantic.ValidationError as e:
                errors = []
                errors_report = report_from_validation_error(e, new_parameters)
                for path, description in errors_report.items():
                    arg = description['invalid_value']
                    error_msg = description['error_message']
                    errors.append(f'[*] Поле: {path}, значение: {arg}, ошибка: {error_msg}')

                gui_error_popup('\n\n'.join(errors))
            except Exception as e:
                # Print the error to console and close the window
                logger.error('Ошибка при сохранении параметров:\n%s', e, exc_info=True)
                break

    window.close()
    del window
