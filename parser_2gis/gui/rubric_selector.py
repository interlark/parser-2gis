from __future__ import annotations

import json
from typing import Any

from ..common import GUI_ENABLED, running_linux
from ..paths import data_path, image_data
from .error_popup import gui_error_popup
from .utils import (ensure_gui_enabled, generate_event_handler,
                    invoke_widget_hook, setup_text_widget)

if GUI_ENABLED:
    import tkinter as tk
    import PySimpleGUI as sg
    from .widgets.sg import RubricsTree
    from .widgets.tk import CustomEntry


def filtered_rubrics(rubrics: dict[str, Any],
                     is_russian: bool = True) -> dict[str, Any]:
    """Filter rubrics on russian/non russian nodes.

    Args:
        rubrics: Loaded rubric dictionary.
        is_russian: Filter criteria.

    Returns:
        Filtered rubric dictionary.
    """
    # Filter nodes
    if is_russian:
        # Rubrics for Russia
        rubrics = {k: v for k, v in rubrics.items() if v.get('isRussian', True)}
    else:
        # Rubrics for Non-russian countries
        rubrics = {k: v for k, v in rubrics.items() if v.get('isNonRussian', True)}

    # Fix references
    for node in rubrics.values():
        node['children'] = [x for x in node['children'] if x in rubrics]

    return rubrics


def create_search_widget(column_element: sg.Element, containing_frame: tk.Frame,
                         toplevel_form: sg.Window) -> tk.Widget:
    """Callback for `custom_widget_hook` that creates and
    returns Search Widget."""
    search_widget = CustomEntry(column_element.TKColFrame, width=60)
    search_widget.pack(side='top', fill='both', expand=True)
    setup_text_widget(search_widget, toplevel_form.TKroot, menu_clear=False)

    search_widget.configure(background=sg.theme_input_background_color(),
                            font=('TkDefaultFont', 12),
                            highlightthickness=0)

    return search_widget


@ensure_gui_enabled
def gui_rubric_selector(is_russian: bool = True) -> dict[str, Any] | None:
    """Run rubric selector.

    Run form that could help user to specify rubric.

    Args:
        is_russian: Whether rubrics for Russia or not.

    Returns:
        Dictionary representing selected rubric
        or `None` if nothing selected.
    """
    # Locate and load rubrics list
    rubric_path = data_path() / 'rubrics.json'
    if not rubric_path.is_file():
        raise FileNotFoundError(f'Файл {rubric_path} не найден')

    try:
        with open(rubric_path, 'r', encoding='utf-8') as f:
            rubrics = filtered_rubrics(json.load(f), is_russian=is_russian)
    except json.JSONDecodeError as e:
        gui_error_popup(f'Файл {rubric_path.name} повреждён:\n{e}')
        return None

    # Window layout
    layout = [
        [
            sg.Text('Поиск рубрики', size=(14, 1)),
            sg.Column([[]], pad=((0, 5), 0), key='-COL_SEARCH-', expand_x=True),
        ],
        [
            RubricsTree(rubrics=rubrics,
                        image_parent=image_data('rubric_folder'),
                        image_item=image_data('rubric_item'),
                        headings=[], auto_size_columns=True,
                        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                        num_rows=30, col0_width=80,
                        key='-TREE-',
                        enable_events=True,
                        expand_x=True, expand_y=True),
        ],
        [
            sg.StatusBar('', size=(0, 1), key='-STATUS-'),
        ],
        [
            sg.Button('OK', size=(6, 1), pad=((6, 7), (7, 7)), key='-BTN_OK-'),
            sg.Button('Отмена', size=(8, 1), pad=((7, 7), (7, 7)), key='-BTN_CANCEL-'),
            sg.Column([
                [
                    sg.Button('Развернуть всё', size=(16, 1), pad=((0, 7), (7, 7)), key='-BTN_EXPAND_ALL-'),
                    sg.Button('Свернуть всё', size=(14, 1), pad=((7, 0), (7, 7)), key='-BTN_COLLAPSE_ALL-'),
                ],
            ], expand_x=True, element_justification='right'),
        ],
    ]

    with invoke_widget_hook(sg.PySimpleGUI, '-COL_SEARCH-', create_search_widget) as get_widget:
        window_title = 'Select rubric' if running_linux() else 'Выбор рубрики'
        window = sg.Window(window_title, layout=layout, finalize=True, auto_size_text=True,
                           font='Any 12', modal=True, keep_on_top=True)

        # Get search widget
        search_widget = get_widget()
        assert search_widget

    # On Linux\MacOS created window could be behind its parent
    window.bring_to_front()

    # Focus on custom widget
    search_widget.focus_set()

    # Hide tree header
    window['-TREE-'].widget.configure(show='tree')

    # Perform rubrics search on text changed
    def perform_rubric_search() -> None:
        query = search_widget.get()
        window['-TREE-'].filter(query)  # noqa: F821

    search_widget.bind('<<Change>>', generate_event_handler(perform_rubric_search))

    # Return rubric
    ret_rubric = None

    # Main loop
    while True:
        event, values = window.read()

        if event in (None, '-BTN_CANCEL-'):
            ret_rubric = None
            break

        elif event == '-BTN_OK-':
            if not ret_rubric:
                gui_error_popup('Рубрика не выбрана!')
                continue
            break

        # Update status bar
        elif event == '-TREE-':
            tree_values = values['-TREE-']
            if tree_values:
                node = rubrics[tree_values[0]]
                is_leaf = not bool(node['children'])
                if is_leaf:
                    ret_rubric = rubrics[tree_values[0]]
                    window['-STATUS-'].update(ret_rubric['label'])
                else:
                    ret_rubric = None
                    window['-STATUS-'].update('')

        elif event == '-BTN_EXPAND_ALL-':
            window['-TREE-'].expand()

        elif event == '-BTN_COLLAPSE_ALL-':
            window['-TREE-'].expand(expand=False)

    window.close()
    del window

    return ret_rubric
