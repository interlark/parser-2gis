from __future__ import annotations

import json

from ..common import GUI_ENABLED, running_linux
from ..paths import data_path
from .error_popup import gui_error_popup
from .rubric_selector import gui_rubric_selector
from .utils import ensure_gui_enabled, setup_text_widget, url_query_encode

if GUI_ENABLED:
    import PySimpleGUI as sg


@ensure_gui_enabled
def gui_urls_generator() -> list[str]:
    """Run URLs generator.

    Run form that can build a bunch of URLs out of query and specified cities.

    Returns:
        List of generated URLs.
    """
    # Locate and load cities list
    cities_path = data_path() / 'cities.json'
    if not cities_path.is_file():
        raise FileNotFoundError(f'Файл {cities_path} не найден')

    try:
        with open(cities_path, 'r', encoding='utf-8') as f:
            cities = json.load(f)
    except json.JSONDecodeError as e:
        gui_error_popup(f'Файл {cities_path.name} повреждён:\n{e}')
        return []

    # Countries available
    default_city_code = 'ru'
    country_code_to_name = dict(
        ae='Объединенные Арабские Эмираты',
        az='Азербайджан', bh='Бахрейн', by='Беларусь', cl='Чили', cy='Кипр', cz='Чехия',
        eg='Египт', it='Италия', kg='Киргизия', kz='Казахстан', om='Оман', qa='Катар',
        ru='Россия', sa='Саудовская Аравия', ua='Украина', uz='Узбекистан')

    country_name_to_code = {v: k for k, v in country_code_to_name.items()}

    # Checkbox layouts
    checkbox_layouts = {}
    for country_code in country_code_to_name.keys():
        layout = []
        for city in cities:
            if city['country_code'] == country_code:
                layout.append([
                    sg.Checkbox(
                        city['name'], metadata=city,
                        checkbox_color=sg.theme_input_background_color())
                ])
        checkbox_layouts[country_code] = sg.Column(
            layout, scrollable=True, vertical_scroll_only=True,
            expand_x=True, expand_y=True, visible=False)

    # Obtain screen dimensions
    _, screen_height = sg.Window.get_screen_size()

    # Window layout
    layout = [
        [
            sg.Column([
                [
                    sg.Text('Запрос', size=(7, 1)),
                    sg.Input(key='-IN_QUERY-'),
                ],
            ]),
        ],
        [
            sg.Column([
                [
                    sg.Text('Страна', size=(7, 1)),
                    sg.Combo(key='-COUNTRY-', default_value=country_code_to_name[default_city_code],
                             values=sorted(country_code_to_name.values()), readonly=True, enable_events=True),
                ],
            ]),
        ],
        [
            sg.Column([
                [
                    sg.Text('Рубрика', size=(7, 1)),
                    sg.Input(key='-IN_RUBRIC-', disabled=True,
                             size=(35, 1), expand_x=True),
                    sg.Column([
                        [
                            sg.Button('...', size=(4, 1), key='-BTN_RUBRIC-'),
                        ],
                    ], element_justification='right', pad=0),
                ],
            ], expand_x=True),
        ],
        [
            sg.Frame('Города', [
                list(checkbox_layouts.values()),
            ], size=(None, int(screen_height / 2)), expand_x=True, expand_y=True),
        ],
        [
            sg.Button('OK', size=(6, 1), pad=((6, 0), (7, 7)), key='-BTN_OK-'),
            sg.Column([
                [
                    sg.Button('Выделить всё', size=(14, 1), pad=((0, 7), (7, 7)), key='-BTN_SELECT_ALL-'),
                    sg.Button('Снять выделение', size=(17, 1), pad=((7, 0), (7, 7)), key='-BTN_DESELECT_ALL-'),
                ],
            ], expand_x=True, element_justification='right'),
        ],
    ]

    window_title = 'Generate links' if running_linux() else 'Сгенерировать ссылки'
    window = sg.Window(window_title, layout=layout, auto_size_text=True,
                       finalize=True, font='Any 12', modal=True, keep_on_top=True)

    setup_text_widget(window['-IN_QUERY-'].widget, window.TKroot,
                      menu_clear=False, set_focus=True)

    setup_text_widget(window['-IN_RUBRIC-'].widget, window.TKroot,
                      menu_clear=False, menu_paste=False, menu_cut=False)

    def update_checkbox_layouts(country_name: str) -> None:
        """Bring frame with checkboxes visible that
        belong to `country_name`.

        Args:
            country_name: Name of a country.
        """
        for country_code, column_element in checkbox_layouts.items():
            if country_code_to_name[country_code] == country_name:
                column_element.update(visible=True)
            else:
                column_element.update(visible=False)

        # Reset rubrics
        rubric_input = window['-IN_RUBRIC-']  # noqa: F821
        rubric_input.metadata = None
        rubric_input.update(value='Без рубрики')

    def select_checkboxes(country_name: str, state: bool = True) -> None:
        """Select all checkboxes that belong to `country_name`.

        Args:
            country_name: Name of a country.
            state: Desired checkboxes' state.
        """
        country_code = country_name_to_code[country_name]
        for element in sum(checkbox_layouts[country_code].Rows, []):
            element.update(state)

    def get_checkboxes(state: bool | None) -> list[sg.Checkbox]:
        """Return all checkboxes.

        Args:
            state: Checkbox state requirement.

        Returns:
            Checkboxes with specified `state`.
        """
        all_checkboxes: list[sg.Checkbox] = sum(sum([x.Rows for x in checkbox_layouts.values()], []), [])
        if isinstance(state, bool):
            all_checkboxes = [x for x in all_checkboxes if x.get() == state]

        return all_checkboxes

    def get_selected_urls(query: str) -> list[str]:
        """Get all checked checkboxes among all frames and generate URLs.

        Args:
            query: User's query.

        Returns:
            List of urls.
        """
        urls = []
        rubric = window['-IN_RUBRIC-'].metadata  # noqa: F821
        for checkbox in get_checkboxes(state=True):
            metadata = checkbox.metadata
            base_url = f'https://2gis.{metadata["domain"]}/{metadata["code"]}'
            rest_url = f'/search/{url_query_encode(query)}'
            if rubric:
                rest_url += f'/rubricId/{rubric["code"]}'

            url = base_url + rest_url
            urls.append(url)

        return urls

    # Set default layout
    update_checkbox_layouts(country_code_to_name[default_city_code])

    # Result urls
    ret_urls = []

    # Main loop
    while True:
        event, values = window.read()

        if event in (None, ):
            break

        elif event == '-COUNTRY-':
            update_checkbox_layouts(values['-COUNTRY-'])

        elif event == '-BTN_SELECT_ALL-':
            select_checkboxes(values['-COUNTRY-'], True)

        elif event == '-BTN_DESELECT_ALL-':
            select_checkboxes(values['-COUNTRY-'], False)

        elif event == '-BTN_RUBRIC-':
            rubric_dict = gui_rubric_selector(is_russian=values['-COUNTRY-'] == 'Россия')
            if rubric_dict:
                rubric_input = window['-IN_RUBRIC-']
                rubric_label = rubric_dict['label']
                rubric_input.update(value=rubric_label)
                if rubric_label == 'Без рубрики':
                    rubric_input.metadata = None
                else:
                    rubric_input.metadata = rubric_dict
                    window['-IN_QUERY-'].update(value=rubric_label)

        elif event == '-BTN_OK-':
            if not values['-IN_QUERY-'].strip():
                gui_error_popup('Необходимо ввести запрос!')
                continue

            if not get_checkboxes(state=True):
                gui_error_popup('Необходимо выбрать хотя бы один город!')
                continue

            ret_urls = get_selected_urls(values['-IN_QUERY-'])
            break

    window.close()
    del window

    return ret_urls
