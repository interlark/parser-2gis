from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Address(BaseModel):
    # Уникальный идентификатор дома, к которому относится данный адрес
    building_id: Optional[str] = None

    # Название здания (в адресе для филиалов)
    building_name: Optional[str] = None

    # Уникальный почтовый код здания
    building_code: Optional[str] = None

    # Почтовый индекс
    postcode: Optional[str] = None

    # Makani адрес объекта
    makani: Optional[str] = None
