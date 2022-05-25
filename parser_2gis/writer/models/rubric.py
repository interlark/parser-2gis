from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Rubric(BaseModel):
    # Уникальный идентификатор рубрики
    id: str

    # Тип рубрики.
    # Возможные значения:
    # * `primary` — основная
    # * `additional` — дополнительная
    kind: str

    # Собственное имя рубрики
    name: str

    # Короткий идентификатор рубрики
    short_id: int

    # Транслированное название страницы в web
    alias: Optional[str] = None

    # Идентификатор объединяющей рубрики
    parent_id: Optional[str] = None
