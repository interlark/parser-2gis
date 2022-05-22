from __future__ import annotations

from typing import TYPE_CHECKING
from ..logger import setup_cli_logger
from ..gui import gui_app

if TYPE_CHECKING:
    from ..config import Configuration


def run_gui(urls: list[str], output_path: str, format: str, config: Configuration) -> None:
    setup_cli_logger(config.log)

    gui_app(urls, output_path, format, config)
