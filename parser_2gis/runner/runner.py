from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import Configuration


class AbstractRunner(ABC):
    def __init__(self, urls: list[str], output_path: str, format: str, config: Configuration):
        self._urls = urls
        self._output_path = output_path
        self._format = format
        self._config = config

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass
