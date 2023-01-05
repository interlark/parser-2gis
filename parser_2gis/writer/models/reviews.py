from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Reviews(BaseModel):
    # Общий рейтинг
    general_rating: Optional[float] = None

    # Общее кол-во отзывов
    general_review_count: Optional[int] = None
