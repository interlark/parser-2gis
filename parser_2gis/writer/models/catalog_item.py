from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


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
    # * `city` — город;
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


class Contact(BaseModel):
    # Тип контакта.
    # Возможные значения:
    # * `email` — электронная почта
    # * `website` — сайт, протокол http
    # * `phone` — телефон
    # * `fax` — факс
    # * `icq` — аккаунт в ICQ
    # * `jabber` — Jabber
    # * `skype` — Skype
    # * `vkontakte` — ВКонтакте
    # * `twitter` — Twitter
    # * `instagram` — Instagram
    # * `facebook` — Facebook
    # * `pobox` — P.O.Box (абонентский ящик)
    # * `youtube` — Youtube
    # * `odnoklassniki` — ok.ru
    # * `googleplus` — Google +
    # * `linkedin` — Linkedin
    # * `pinterest` — Pinterest
    # * `whatsapp` — Whatsapp
    # * `telegram` — Telegram
    # * `viber` — Viber
    type: str

    # Техническое значение контакта (например "Телефон в международном формате")
    value: str

    # Значение контакта для вывода на экран (например "e-mail Иванова")
    text: Optional[str] = None

    # Ссылка на сайт или социальную сеть
    url: Optional[str] = None

    # Значение контакта для вывода на принтер (например "e-mail Иванова")
    print_text: Optional[str] = None

    # Уточняющая информация о контакте (например "для деловой переписки")
    comment: Optional[str] = None


class ContactGroup(BaseModel):
    # Список контактов
    contacts: List[Contact]

    # Расписание группы контактов
    schedule: Optional[Schedule] = None

    # Комментарий к группе контактов (например "Многокональный телефон")
    comment: Optional[str] = None

    # Имя группы контактов (например "Сервисный центр")
    name: Optional[str] = None


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


class Org(BaseModel):
    # Идентификатор
    id: str

    # Собственное имя организации
    name: str

    # Количество филиалов данной организации
    branch_count: int


class Point(BaseModel):
    # Широта
    lat: float

    # Долгота
    lon: float


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


class WorkingHour(BaseModel):
    # Значение в формате hh:mm
    from_: str = Field(..., alias='from')

    # Значение в формате hh:mm
    to: str


class ScheduleDay(BaseModel):
    # Часы работы
    working_hours: List[WorkingHour]


class Schedule(BaseModel):
    # Понедельник
    Mon: Optional[ScheduleDay] = None

    # Вторник
    Tue: Optional[ScheduleDay] = None

    # Среда
    Wed: Optional[ScheduleDay] = None

    # Четверг
    Thu: Optional[ScheduleDay] = None

    # Пятница
    Fri: Optional[ScheduleDay] = None

    # Суббота
    Sat: Optional[ScheduleDay] = None

    # Воскресенье
    Sun: Optional[ScheduleDay] = None

    # Признак того, что организация работает круглосуточно 7 дней в неделю.
    # Если поле отсутствует, то организация не считается работающей круглосуточно.
    is_24x7: Optional[bool] = None

    # Локализованное описание возможных изменений во времени работы.
    # Применяется для праздников, временных ограничений и т.д.
    description: Optional[str] = None

    # Комментарий (например "Кругосуточно в праздничные дни")
    comment: Optional[str] = None

    # Дата начала изменений в расписании работы. Формат: "YYYY-MM-DD"
    date_from: Optional[str] = None

    # Дата конца изменений в расписании работы. Формат: "YYYY-MM-DD"
    date_to: Optional[str] = None

    def to_str(self, join_char: str, add_comment: bool = False) -> str:
        """Schedule as a string.

        Args:
            join_char: Char for splitting split days.
            add_comment: Whether to add comment at the end.

        Returns:
            Schedule as a string.
        """
        days_names = [x.name for x in self.__fields__.values() if x.type_ == ScheduleDay]
        days_mapping = dict(Mon='Пн', Tue='Вт', Wed='Ср', Thu='Чт', Fri='Пт', Sat='Сб', Sun='Вс')

        slots_list = []
        for day_name in days_names:
            day_value = getattr(self, day_name)
            if not day_value:
                continue

            day_slot = f'{days_mapping[day_name]}: '
            for i, time_slot in enumerate(day_value.working_hours):
                if i > 0:
                    day_slot += ', '
                day_slot += f'{time_slot.from_}-{time_slot.to}'

            slots_list.append(day_slot)

        result = join_char.join(slots_list)
        if add_comment and self.comment:
            result += ' (%s)' % self.comment

        return result


class CatalogItem(BaseModel):
    # Уникальный идентификатор филиала организации (например "141265769336625_f91d4H3777058262347790J0e8g28765")
    id: str

    # Адрес объекта
    address: Optional[Address] = None

    # Уточнение о местоположении филиала по указанному адресу (например "офис 413")
    address_comment: Optional[str] = None

    # Представление поля address в виде одной строки (например "Димитрова проспект, 7")
    address_name: Optional[str] = None

    # Принадлежность к административной территории
    adm_div: List[AdmDivItem] = []

    # Алиас города, в котором находится объект (например "perm")
    city_alias: Optional[str] = None

    # Контакты филиала
    contact_groups: List[ContactGroup] = []

    # Текущая локаль для региона (например "ru_RU")
    locale: str

    # Полное собственное название филиала или название организации (например "Солнышко, кафе")
    name: Optional[str] = None

    # Расширеное название филиала
    name_ex: NameEx

    # Организация
    org: Org

    # Координаты точки поиска, заданные в системе координат WGS84 в формате lon, lat
    point: Optional[Point] = None

    # Уникальный идентификатор проекта
    region_id: Optional[str] = None

    # Уникальный идентификатор сегмента
    segment_id: Optional[str] = None

    # Рубрики филиала
    rubrics: List[Rubric]

    # Время работы
    schedule: Optional[Schedule] = None

    # Смещение таймзоны в минутах относительно UTC0 (например "420")
    timezone_offset: Optional[int] = None

    # Тип объекта
    type: str

    # Признак удаленного объекта
    is_deleted: Optional[bool]

    @property
    def url(self) -> str:
        return 'https://2gis.com/firm/%s' % self.id.split('_')[0]
