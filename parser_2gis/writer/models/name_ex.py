from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class NameEx(BaseModel):
    # Собственное имя филиала
    primary: str

    # Расширение имени филиала (например "кафе")
    extension: Optional[str] = None

    # Юридическое название филиала (например "ООО Солнышко")
    legal_name: Optional[str] = None

    # Описание филиала (например "Склад")
    description: Optional[str] = None

    # Короткое имя на карте
    short_name: Optional[str] = None

    # Дополнительная информация к названию филиала,
    # которая должна быть показана в развёрнутой карточке
    addition: Optional[str] = None
