from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Flags(BaseModel):
    # Заполняется только для type=city и принимает единственное значение true в случае,
    # если город является главным городом текущего проекта (например Новосибирск)
    is_default: Optional[bool] = None

    # Заполняется только для type=adm_div, subtype=city|settlement
    # и принимает единственное значение true в случае, если населённый пункт является районным центром.
    is_district_area_center: Optional[bool] = None

    # Заполняется только для type=adm_div, subtype=city|settlement
    # и принимает единственное значение true в случае, если населённый пункт является областным центром.
    is_region_center: Optional[bool] = None

    # Cтрока, наличие которой говорит о том, что филиал временно не работает.
    # В строке выгружается код причины закрытия.
    temporary_closed: Optional[str] = None


class AdmDivItem(BaseModel):
    # Идентификатор объекта административной единицы
    id: Optional[str] = None

    # Имя объекта
    name: str

    # Название территории (для использования в функционале «поделиться»,
    # для конечных точек маршрута и т.д.).
    caption: Optional[str] = None

    # Тип объекта административной единицы.
    # Возможные значения:
    # * `city` — город
    # * `settlement` — населённый пункт
    # * `division` — округ
    # * `district` — район
    # * `living_area` — жилмассив, микрорайон
    # * `place` — место
    # * `district_area` — район области
    # * `region` — регион (область/край/республика и т.п.)
    # * `country` - страна
    type: str

    # Алиас города, в котором находится объект
    city_alias: Optional[str] = None

    # Дополнительные флаги
    flags: Optional[Flags] = None

    # Заполняется только для type=city и принимает единственное значение
    # true в случае, если город является главным городом текущего проекта (например "Новосибирск")
    is_default: Optional[bool] = None

    # Детализированный тип административно-территориальной единицы.
    # Возможные значения:
    # * `city` — город
    # * `microdistrict` — микрорайон
    # * `residential_district` — жилмассив
    # * `residential_quarter` — квартал
    # * `poselok` — посёлок
    # * `residential_complex` — жилой комплекс
    # * `selo` — село
    # * `derevnja` — деревня
    # * `cottage_estate` — коттеджный посёлок
    # * `urban_settlement` — посёлок городского типа
    # * `workers_settlement` — рабочий посёлок
    # * `dacha_settlement` — дачный посёлок
    # * `resort_settlement` — курортный посёлок
    # * `stanitsa` — станица
    # * `sloboda` — слобода
    # * `khutor` — хутор
    # * `aul` — аул
    # * `aal` — аал
    # * `town` — (военный) городок
    # * `farmstead` — заимка
    # * `vyselok` — выселок
    # * `municipality` — муниципальное образование
    # * `station` — станция
    # * `townhouse_settlement` — посёлок таунхаусов
    # * `territory` — территория
    # * `cooperative` — кооператив
    # * `partnership` — товарищество
    detailed_subtype: Optional[str] = None
