from __future__ import annotations

import tkinter as tk

from .custom_text import CustomText


class TextLineNumbers(tk.Canvas):
    """Numbered Line Widget."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.textwidget: tk.Text | None = None

    def attach(self, textwidget: tk.Text) -> None:
        self.textwidget = textwidget

    def redraw(self) -> None:
        self.delete('all')

        assert self.textwidget, 'Attach textwidget first'
        i = self.textwidget.index('@0,0')
        while True:
            bbox = self.textwidget.dlineinfo(i)
            if bbox is None:
                break

            y = bbox[1]
            line_n = f'{i}'.split('.')[0]

            self.create_text(2, y, anchor='nw', text=line_n, font=('TkDefaultFont', 12))
            i = self.textwidget.index(f'{i}+1line')


class LineNumberedText(tk.Frame):
    """Combined Numbered Line and Customized Text Widgets."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.text = CustomText(self)

        self.vsb = tk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.hsb = tk.Scrollbar(self, orient='horizontal', command=self.text.xview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.text.configure(xscrollcommand=self.hsb.set)
        self.text.configure(wrap='none', undo=True)

        self.linenumbers = TextLineNumbers(self, width=34)
        self.linenumbers.attach(self.text)

        self.vsb.pack(side='right', fill='y')
        self.hsb.pack(side='bottom', fill='x')
        self.linenumbers.pack(side='left', fill='y')
        self.text.pack(side='right', fill='both', expand=True)

        self.text.bind('<<Change>>', self._on_change)
        self.text.bind('<Configure>', self._on_change)

    def _on_change(self, event: tk.Event) -> None:
        self.linenumbers.redraw()
