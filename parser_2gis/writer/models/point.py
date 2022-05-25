from __future__ import annotations

from pydantic import BaseModel


class Point(BaseModel):
    # Широта
    lat: float

    # Долгота
    lon: float
