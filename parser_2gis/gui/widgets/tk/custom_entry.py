from __future__ import annotations

import tkinter as tk
from typing import Any


class CustomEntry(tk.Entry):
    """Custom entry widget that report on internal widget commands."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Create a proxy for the underlying widget
        widget_name = self._w  # type: ignore[attr-defined]
        self._orig = widget_name + '_orig'
        self.tk.call('rename', widget_name, self._orig)
        self.tk.createcommand(widget_name, self._proxy)

    def _proxy(self, command: Any, *args) -> Any:
        # Let the actual widget perform the requested action
        cmd = (self._orig, command) + args

        try:
            result = self.tk.call(cmd)
        except tk.TclError:
            result = ''

        # Generate an event if something was added or deleted
        if command in ('insert', 'delete', 'replace'):
            self.event_generate('<<Change>>', when='tail')

        return result
