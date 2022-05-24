from __future__ import annotations

import contextlib
import functools
import urllib.parse
from typing import TYPE_CHECKING, Any, Callable, TypeVar, cast

from ..common import GUI_ENABLED, running_mac

F = TypeVar('F', bound=Callable[..., Any])

if TYPE_CHECKING:
    import tkinter as tk

if GUI_ENABLED:
    import tkinter as tk  # noqa: F811
    import PySimpleGUI as sg


def generate_event_handler(func: Callable, with_break: bool = False) -> Callable:
    """Generate event handler out of function.

    Args:
        func: Function to be wrapped in event handler.
        with_break: Whether to stop event propagation.

    Returns:
        Event handler.
    """
    def wrapper(event: tk.Event) -> str | None:
        func()
        return 'break' if with_break else None

    return wrapper


def setup_text_widget(widget: tk.Text | tk.Entry, root: tk.Toplevel, *,
                      menu_copy: bool = True, menu_paste: bool = True,
                      menu_cut: bool = True, menu_clear: bool = True,
                      set_focus: bool = False) -> None:
    """Setup text widgets, add context menu and other functionality.

    Args:
        widget: tk.Text or tk.Entry widget.
        root: Parent window.
        menu_copy: Whether text of the `widget` could be copied with context menu.
        menu_paste: Whether text of the `widget` could be pasted with context menu.
        menu_cut: Whether text of the `widget` could be cut with context menu.
        menu_clear: Whether text of the `widget` could be cleared with context menu.
        set_focus: Whether to set focus on the `widget`.
    """
    # def get_text() -> str:
    #     if isinstance(widget, tk.Entry):
    #         return widget.get()
    #     elif isinstance(widget, tk.Text):
    #         return widget.get('1.0','end')
    #     return ''

    def get_clipboard() -> str | None:
        try:
            return widget.clipboard_get()
        except tk.TclError:
            # Nothing in clipboard
            return None

    def get_selection() -> str | None:
        if isinstance(widget, tk.Entry):
            if widget.selection_present():
                return widget.selection_get()
            else:
                return None
        elif isinstance(widget, tk.Text):
            try:
                return widget.get('sel.first', 'sel.last')
            except tk.TclError:
                # Nothing was selected
                return None

    def delete_selection() -> None:
        try:
            widget.delete('sel.first', 'sel.last')  # Works for tk.Entry and tk.Text
        except tk.TclError:
            # Nothing was selected
            pass

    def copy_text() -> None:
        selection = get_selection()
        if selection:
            widget.clipboard_clear()
            widget.clipboard_append(selection)
            widget.update()

    def paste_text() -> None:
        delete_selection()

        clipboard = get_clipboard()
        if clipboard:
            widget.insert('insert', clipboard)

    def cut_text() -> None:
        copy_text()
        delete_selection()

    def clear_text() -> None:
        widget.delete('1.0', 'end')

    def select_all() -> None:
        if isinstance(widget, tk.Entry):
            widget.select_range(0, 'end')
            widget.icursor('end')
        elif isinstance(widget, tk.Text):
            widget.tag_add('sel', '1.0', 'end')

    # Create menu
    menu = tk.Menu(root, tearoff=False)

    if menu_cut:
        menu.add_command(label='Вырезать', command=cut_text)
    if menu_copy:
        menu.add_command(label='Скопировать', command=copy_text)
    if menu_paste:
        menu.add_command(label='Вставить', command=paste_text)
        # Fix paste bahaviour
        widget.bind('<<Paste>>', generate_event_handler(paste_text, with_break=True))

    # Select all bahaviour
    widget.bind('<Control-a>', generate_event_handler(select_all, with_break=True))
    menu.add_command(label='Выделить всё', command=select_all)

    if menu_clear:
        menu.add_command(label='Очистить', command=clear_text)

    # Show menu
    def show_menu_handler(event: tk.Event) -> None:
        """Config menu."""
        is_readonly = widget.cget('state') == 'readonly'

        if menu_copy:
            copy_state = 'normal' if get_selection() else 'disabled'
            menu.entryconfig('Скопировать', state=copy_state)
        if menu_paste:
            paste_state = 'normal' if not is_readonly and get_clipboard() else 'disabled'
            menu.entryconfig('Вставить', state=paste_state)
        if menu_cut:
            cut_state = 'normal' if not is_readonly and get_selection() else 'disabled'
            menu.entryconfig('Вырезать', state=cut_state)
        if menu_clear:
            clear_state = 'normal' if not is_readonly else 'disabled'
            menu.entryconfig('Очистить', state=clear_state)

        menu.post(event.x_root, event.y_root)
        menu.focus_set()

    rclick_event_name = '<Button-2>' if running_mac() else '<Button-3>'
    widget.bind(rclick_event_name, show_menu_handler)

    # Hide menu
    menu.bind('<FocusOut>', generate_event_handler(menu.unpost))

    # Focus
    if set_focus:
        widget.focus_set()


def ensure_gui_enabled(func: F) -> F:
    """Decorator to be sure GUI is enabled
    before decorated form is run."""
    @functools.wraps(func)
    def _ensure_gui_enabled(*args, **kwargs) -> Any:
        assert GUI_ENABLED, 'GUI is not enabled'
        return func(*args, **kwargs)

    return cast(F, _ensure_gui_enabled)


@contextlib.contextmanager
def invoke_widget_hook(sg: sg, parent_key: str,
                       widget_callback: Callable[[sg.Element, tk.Frame, sg.Window], tk.Widget]):
    """Hacky way to place custom widget inside element with key `parent_key`
    by hooking SG module function PackFormIntoFrame during window finalization.

    Args:
        sg: PySimpleGUI module
        parent_key: Parent element key.
        created_widget: Callback with just created parent element as an argument.

    Returns:
        Patched SG with `widget_callback` hook.
    """
    old_PackFormIntoFrame = sg.PackFormIntoFrame
    created_widget = None

    def new_PackFormIntoFrame(form, containing_frame, toplevel_form) -> None:
        nonlocal created_widget
        if hasattr(form, 'Key') and form.Key == parent_key:
            created_widget = widget_callback(form, containing_frame, toplevel_form)
        old_PackFormIntoFrame(form, containing_frame, toplevel_form)

    def get_widget() -> tk.Widget | None:
        return created_widget

    sg.PackFormIntoFrame = new_PackFormIntoFrame
    yield get_widget
    sg.PackFormIntoFrame = old_PackFormIntoFrame


def url_query_encode(url: str) -> str:
    """URL encode for query, nonascii
    regular russian characters allowed (plus space).

    Args:
        url: URL to be encoded.

    Returns:
        Encoded URL.
    """
    encoded_characters = []
    for char in url:
        char_ord = ord(char.lower())

        # Do not escape [а-яё ]
        if 1072 <= char_ord <= 1103 \
           or char_ord in (1105, 32):
            encoded_characters.append(char)
        else:
            encoded_characters.append(urllib.parse.quote(char, safe=''))

    return ''.join(encoded_characters)
