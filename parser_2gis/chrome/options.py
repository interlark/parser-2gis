from __future__ import annotations

import pathlib
from typing import Optional

import psutil
from pydantic import BaseModel, PositiveInt

from ..common import floor_to_hundreds


def default_memory_limit() -> int:
    """Default memory limit for V8, 0.75 of total physical memory."""
    memory_total = psutil.virtual_memory().total / 1024 ** 2  # MB
    return floor_to_hundreds(round(0.75 * memory_total))


class ChromeOptions(BaseModel):
    """Represents all possible options for Chrome.

    Attributes:
        binary_path: Chrome binary path. If not set, tries to find automatically.
        start_maximized: Start browser maximized.
        headless: Start browser hidden, without GUI.
        disable_images: Disable images.
        silent_browser: Do not show Chrome's output in `stdout`.
        memory_size: Max V8's memory size.
    """
    binary_path: Optional[pathlib.Path]
    start_maximized: bool = False
    headless: bool = True
    disable_images: bool = True
    silent_browser: bool = True
    memory_limit: PositiveInt = default_memory_limit()
