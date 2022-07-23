from __future__ import annotations

from typing import TYPE_CHECKING

from ..logger import setup_cli_logger
from ..runner import CLIRunner

if TYPE_CHECKING:
    from ..config import Configuration


def cli_app(urls: list[str], output_path: str, format: str, config: Configuration) -> None:
    setup_cli_logger(config.log)

    runner = CLIRunner(urls, output_path, format, config)
    runner.start()
