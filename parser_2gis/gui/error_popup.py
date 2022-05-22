from __future__ import annotations

import textwrap

from ..common import GUI_ENABLED, running_linux
from ..paths import image_data
from .utils import ensure_gui_enabled

if GUI_ENABLED:
    import PySimpleGUI as sg


@ensure_gui_enabled
def gui_error_popup(error_msg: str) -> None:
    """Run error modal window.

    Args:
        error_msg: Error message.
    """
    # App color theme
    sg.theme('Green')

    # Set icon
    sg.set_global_icon(image_data('icon', 'png'))

    # Adjust error message width
    error_msg = '\n'.join(
        textwrap.wrap(error_msg, width=60, replace_whitespace=False, break_on_hyphens=False)
    )

    # Window layout
    layout = [
        [
            sg.Text(error_msg),
        ],
        [
            sg.Column([
                [
                    sg.Button('Закрыть', key='-BTN_CLOSE-', size=(8, 1), button_color='firebrick3',
                              focus=True, bind_return_key=True, pad=((0, 0), 3)),
                ],
            ], expand_x=True, element_justification='center'),
        ],
    ]

    window_title = 'Error' if running_linux() else 'Ошибка'
    window = sg.Window(window_title, layout, auto_size_text=True, finalize=True,
                       font='Any 12', modal=True, keep_on_top=True)

    while True:
        event, _ = window.Read()

        # Close window
        if event in (None, '-BTN_CLOSE-'):
            break

    window.close()
    del window
