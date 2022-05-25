from __future__ import annotations

from pydantic import BaseModel


class Org(BaseModel):
    # Идентификатор
    id: str

    # Собственное имя организации
    name: str

    # Количество филиалов данной организации
    branch_count: int
