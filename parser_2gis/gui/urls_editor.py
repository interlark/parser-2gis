from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import GUI_ENABLED
from .urls_generator import gui_urls_generator
from .utils import ensure_gui_enabled, invoke_widget_hook, setup_text_widget

if TYPE_CHECKING:
    import tkinter as tk

if GUI_ENABLED:
    import PySimpleGUI as sg
    from .widgets.tk import LineNumberedText


def create_text_widget(column_element: sg.Element, containing_frame: tk.Frame,
                       toplevel_form: sg.Window) -> tk.Widget:
    """Callback for `custom_widget_hook` that creates and
    returns Line Numbered Text Widget."""
    # Create and setup Line Numbered Text Widget
    urls_widget = LineNumberedText(column_element.TKColFrame)
    urls_widget.pack(side='top', fill='both', expand=True)
    urls_widget.text.configure(background=sg.theme_input_background_color(),
                               font=('TkDefaultFont', 12),
                               highlightthickness=0)

    setup_text_widget(urls_widget.text, toplevel_form.TKroot)
    return urls_widget


@ensure_gui_enabled
def gui_urls_editor(urls: list[str]) -> list[str] | None:
    """Run URLs editor.

    Args:
        urls: Currently set urls.

    Returns:
        List of URLs or `None` on cancel.
    """
    # Window layout
    layout = [
        [
            sg.Text('Ссылки'),
        ],
        [
            sg.Column([[]], key='-COL_URLS-', size=(0, 0,), expand_x=True, expand_y=True),
        ],
        [
            sg.Button('OK', size=(6, 1), pad=((5, 7), (7, 7)), key='-BTN_OK-'),
            sg.Button('Сгенерировать', size=(15, 1), pad=((7, 7), (7, 7)), key='-BTN_BUILD-'),
            sg.Column([
                [
                    sg.Button('Отмена', size=(8, 1), pad=(0, (7, 7)), key='-BTN_CANCEL-'),
                ],
            ], expand_x=True, element_justification='right'),
        ],
    ]

    with invoke_widget_hook(sg.PySimpleGUI, '-COL_URLS-', create_text_widget) as get_widget:
        window = sg.Window('URLs', layout=layout, finalize=True, auto_size_text=True,
                           font='Any 12', modal=True, keep_on_top=True)

        # Get `LineNumberedText` widget
        urls_widget = get_widget()
        assert urls_widget

    # Insert existing links
    urls_widget.text.insert('insert', '\n'.join(urls))

    # Focus on custom widget
    urls_widget.text.focus_set()

    # Result urls
    ret_urls = None

    # Main loop
    while True:
        event, _ = window.read()
        if event in (None, '-BTN_CANCEL-'):
            break

        elif event == '-BTN_BUILD-':
            urls = gui_urls_generator()
            if urls:
                urls_content = urls_widget.text.get('1.0', 'end')[:-1]
                join_character = '\n' if urls_content and urls_content[-1:] != '\n' else ''
                urls_widget.text.insert('end', join_character + '\n'.join(urls))

        elif event == '-BTN_OK-':
            urls_content = urls_widget.text.get('1.0', 'end')[:-1]
            ret_urls = [x for x in urls_content.splitlines() if x.strip()]
            break

    window.close()
    del window

    return ret_urls
