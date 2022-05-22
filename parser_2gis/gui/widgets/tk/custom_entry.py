import tkinter as tk


class CustomEntry(tk.Entry):
    def __init__(self, *args, **kwargs):
        """An entry widget that report on internal widget commands."""
        tk.Entry.__init__(self, *args, **kwargs)

        # Create a proxy for the underlying widget
        self._orig = self._w + '_orig'
        self.tk.call('rename', self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args

        try:
            result = self.tk.call(cmd)
        except tk.TclError:
            return ''

        # Generate an event if something was added or deleted
        if command in ('insert', 'delete', 'replace'):
            self.event_generate('<<Change>>', when='tail')

        return result
