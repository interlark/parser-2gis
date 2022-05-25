from __future__ import annotations

import queue
import threading
import webbrowser
from functools import partial
from typing import TYPE_CHECKING, Tuple

from ..common import GUI_ENABLED, running_linux, running_windows
from ..exceptions import ChromeRuntimeException, ChromeUserAbortException
from ..logger import logger, setup_gui_logger
from ..parser import Parser2GIS
from ..paths import image_data, image_path
from ..version import version
from ..writer import get_writer
from .error_popup import gui_error_popup
from .settings import gui_settings
from .urls_editor import gui_urls_editor
from .utils import (ensure_gui_enabled, generate_event_handler,
                    setup_text_widget)

if TYPE_CHECKING:
    from ..config import Configuration

if GUI_ENABLED:
    import tkinter as tk
    import PySimpleGUI as sg


class ParsingThread(threading.Thread):
    """Parsing thread.

    Args:
        urls: 2GIS URLs with result items to be collected.
        output_path: Path to the result file.
        format: `csv` or `json` format.
        config: Configuration.
    """
    def __init__(self, urls: list[str], output_path: str, format: str,
                 config: Configuration, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._urls = urls
        self._output_path = output_path
        self._format = format
        self._config = config
        self._parser: Parser2GIS | None = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start thread."""
        self._stopped = False
        logger.info('Парсинг запущен.')
        super().start()

    def stop(self) -> None:
        """Stop thread."""
        if not self._started.is_set():  # type: ignore
            raise RuntimeError('start() is not called')

        if self._stopped:
            return  # We can stop the thread only once

        self._stopped = True
        self._stop_parser()

    def _stop_parser(self) -> None:
        """Close parser if it's been open."""
        with self._lock:
            if self._parser:
                self._parser.close()
                self._parser = None

    def run(self) -> None:
        """Thread's activity."""
        try:
            with get_writer(self._output_path, self._format, self._config.writer) as writer:
                for url in self._urls:
                    self._parser = Parser2GIS(chrome_options=self._config.chrome,
                                              parser_options=self._config.parser)
                    if not self._stopped:
                        logger.info(f'Парсинг ссылки {url}')
                        try:
                            self._parser.parse_url(url, writer)
                        finally:
                            logger.info('Парсинг ссылки завершён.')
                    else:
                        break

                    self._stop_parser()
        except Exception as e:
            if not self._stopped:  # Don't catch intended exceptions caused by stopping parser
                if isinstance(e, ChromeRuntimeException) and str(e) == 'Tab has been stopped':
                    logger.error('Вкладка браузера была закрыта.')
                elif isinstance(e, ChromeUserAbortException):
                    logger.error('Работа парсера прервана пользователем.')
                else:
                    logger.error('Ошибка во время работы парсера.', exc_info=True)
        finally:
            self._stop_parser()
            logger.info('Парсинг завершён.')


@ensure_gui_enabled
def gui_app(urls: list[str], output_path: str, format: str, config: Configuration) -> None:
    """Run GUI.

    Args:
        url: 2GIS URLs with results to be collected.
        output_path: Path to the result file.
        format: `csv` or `json` format.
        config: User configuration.
    """
    # App color theme
    sg.theme('Green')

    # Set icon
    sg.set_global_icon(image_data('icon', 'png'))

    # Result format
    default_result_format = format if format else 'csv'
    result_filetype = {'csv': [('CSV Table', '*.csv')], 'json': [('JSON', '*.json')]}

    # If urls wasn't passed then let it be an empty list
    if urls is None:
        urls = []

    # Window layout
    layout = [
        [
            sg.Text('URL', size=(4, 1)),
            sg.Input(key='-IN_URL-', use_readonly_for_disable=True, expand_x=True),
            sg.Button('...', size=(4, 1), key='-BTN_URLS-'),
            sg.Button('', image_data=image_data('settings'), key='-BTN_SETTINGS-', tooltip=str(config.path)),
        ],
        [
            sg.Frame('Результат', expand_x=True, expand_y=True, layout=[
                [
                    sg.Column([
                        [
                            sg.Text('Тип'),
                            sg.Combo(key='-FILE_FORMAT-', default_value=default_result_format,
                                     values=['csv', 'json'], readonly=True, enable_events=True),
                            sg.Text('Путь'),
                            sg.Input(key='-OUTPUT_PATH-', expand_x=True,
                                     default_text='' if output_path is None else output_path),
                            sg.FileSaveAs(key='-OUTPUT_PATH_BROWSE-', button_text='Обзор', size=(7, 1),
                                          default_extension=f'.{default_result_format}',
                                          file_types=result_filetype[default_result_format]),
                        ],
                    ], expand_x=True),
                ],
            ]),
        ],
        [
            sg.Frame('Лог', expand_x=True, expand_y=True, layout=[
                [
                    sg.Multiline(key='-LOG-', size=(80, 20), expand_x=True, autoscroll=True,
                                 reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True),
                ],
            ]),
        ],
        [
            sg.Image(data=image_data('logo'), key='-IMG_LOGO-',
                     enable_events=True, background_color=sg.theme_background_color()),
            sg.Text(f'v{version}'),
            sg.Column([
                [
                    sg.Image(key='-IMG_LOADING-', visible=False, background_color=sg.theme_background_color()),
                ],
            ], expand_x=True, element_justification='right'),
            sg.Column([
                [
                    sg.Button('Запуск', key='-BTN_START-', size=(8, 1)),
                    sg.Button('Стоп', key='-BTN_STOP-', size=(6, 1), button_color=('white', 'orange3'), visible=False),
                ],
            ], element_justification='right'),
            sg.Button('Выход', size=(7, 1), button_color=('white', 'firebrick3'), key='-BTN_EXIT-'),
        ],
    ]

    # tkinter could encounter encoding problem with cyrillics characters on linux systems (toolbar, topbar),
    # so let the window titles be in English. No big deal, actually.
    window_title = 'Parser 2GIS' if running_linux() else 'Парсер 2GIS'

    # Main window
    window = sg.Window(window_title, layout, auto_size_text=True, finalize=True, font='Any 12')

    # Setup text widgets
    setup_text_widget(window['-IN_URL-'].widget, window.TKroot, menu_clear=False, set_focus=True)
    setup_text_widget(window['-OUTPUT_PATH-'].widget, window.TKroot, menu_clear=False)
    setup_text_widget(window['-LOG-'].widget, window.TKroot, menu_paste=False, menu_cut=False)

    # Forbid user to edit output console,
    # block any keys except ctl+c, ←, ↑, →, ↓
    def log_key_handler(e: tk.Event) -> str | None:
        if e.char == '\x03' or e.keysym in ('Left', 'Up', 'Right', 'Down'):
            return None

        return 'break'

    window['-LOG-'].widget.bind('<Key>', log_key_handler)

    # Enable logging queue to be able to handle log in the mainloop
    log_queue: queue.Queue[Tuple[str, str]] = queue.Queue()  # Queue of log messages (log_level, log_message)
    setup_gui_logger(log_queue, config.log)

    # Hand cursor for logo
    window['-IMG_LOGO-'].widget.config(cursor='hand2')

    # Set config settings button hover/click image
    def change_settings_image(image_name: str) -> None:
        window['-BTN_SETTINGS-'].update(image_data=image_data(image_name))  # noqa: F821

    window['-BTN_SETTINGS-'].TKButton.bind(
        '<Button>' if running_windows() else '<Enter>',
        generate_event_handler(partial(change_settings_image, 'settings_inverted')))

    window['-BTN_SETTINGS-'].TKButton.bind(
        '<ButtonRelease>' if running_windows() else '<Leave>',
        generate_event_handler(partial(change_settings_image, 'settings')))

    # Move cursor to the end of the URL input
    window['-IN_URL-'].widget.icursor('end')

    # Parsing thread
    parsing_thread: ParsingThread | None = None

    def parsing_thread_running() -> bool:
        return parsing_thread is not None and parsing_thread.is_alive()

    # Update URL Input element according to `urls` list
    def update_urls_input() -> None:
        urls_length = len(urls) if isinstance(urls, list) else 0
        if urls_length == 0:
            window['-IN_URL-'].update('', disabled=False)  # noqa: F821
        elif urls_length == 1:
            window['-IN_URL-'].update(urls[0], disabled=False)  # noqa: F821
        else:
            def get_plural() -> str:
                last_1d = urls_length % 10
                last_2d = urls_length % 100
                if 11 <= last_2d <= 19:
                    return 'ссылок'
                if last_1d == 1:
                    return 'ссылка'
                elif 2 <= last_1d <= 4:
                    return 'ссылки'
                return 'ссылок'

            window['-IN_URL-'].update(f'<{len(urls)} {get_plural()}>', disabled=True)  # noqa: F821

    update_urls_input()

    # Set log background colors by level
    log_colors = dict(CRITICAL='tomato1', ERROR='tomato1', WARNING='tan1')

    # Pre-define log tags
    for color in log_colors.values():
        tag = f'Multiline(None,{color},None)'
        window['-LOG-'].tags.add(tag)
        window['-LOG-'].widget.tag_configure(tag, background=color)

    # Keep selection tag priority on top
    window['-LOG-'].widget.tag_raise('sel')

    # Main loop
    while True:
        event, values = window.Read(timeout=50)

        # App exit
        if event in (None, '-BTN_EXIT-'):
            if parsing_thread_running():
                assert parsing_thread
                parsing_thread.stop()
                parsing_thread.join()

            break

        # Run settings
        elif event == '-BTN_SETTINGS-':
            gui_settings(config)

        # Run URLs Editor
        elif event == '-BTN_URLS-':
            # Sync urls with input element
            if not window['-IN_URL-'].Disabled:
                urls = [values['-IN_URL-']]

            ret_urls = gui_urls_editor(urls)
            if ret_urls is not None:
                urls = ret_urls
                update_urls_input()

        # Click logo
        elif event == '-IMG_LOGO-':
            webbrowser.open('https://github.com/interlark/parser-2gis')

        # Click stop
        elif event == '-BTN_STOP-':
            if parsing_thread_running():
                logger.warn('Парсинг остановлен пользователем.')
                assert parsing_thread
                parsing_thread.stop()

                # Disable button until the thread fully stops
                window['-BTN_STOP-'].update(disabled=True)

        # Click start
        elif event == '-BTN_START-':
            # Check output file path
            if not values['-OUTPUT_PATH-']:
                gui_error_popup('Отсутствует путь результирующего файла!')
                continue

            # Check output file path
            if not values['-IN_URL-']:
                gui_error_popup('Отсутствует URL!')
                continue

            # Check result format
            if values['-FILE_FORMAT-'] not in ('csv', 'json'):
                gui_error_popup('Формат результирующего файла должен быть csv или json!')
                continue

            # Sync urls with input element
            if not window['-IN_URL-'].Disabled:
                urls = [values['-IN_URL-']]

            # Run parser
            if not parsing_thread_running():
                parsing_thread = ParsingThread(urls, values['-OUTPUT_PATH-'], values['-FILE_FORMAT-'], config)
                parsing_thread.start()

                # Activate stop button if it's been disabled
                window['-BTN_STOP-'].update(disabled=False)

        # Poll log queue
        while True:
            try:
                log_level, log_msg = log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                # Print message to log
                window['-LOG-'].update(log_msg, append=True,
                                       background_color_for_value=log_colors.get(log_level, None))

        # Swap start/stop buttons
        if parsing_thread_running():
            if window['-BTN_START-'].visible:
                window['-BTN_START-'].update(visible=False)

            if not window['-BTN_STOP-'].visible:
                window['-BTN_STOP-'].update(visible=True)

            if not window['-IMG_LOADING-'].visible:
                window['-IMG_LOADING-'].update(visible=True)

            # Run loading animation
            window['-IMG_LOADING-'].update_animation(image_path('loading'), time_between_frames=50)
        else:
            if not window['-BTN_START-'].visible:
                window['-BTN_START-'].update(visible=True)

            if window['-BTN_STOP-'].visible:
                window['-BTN_STOP-'].update(visible=False)

            if window['-IMG_LOADING-'].visible:
                window['-IMG_LOADING-'].update(visible=False)

    window.close()
    del window
