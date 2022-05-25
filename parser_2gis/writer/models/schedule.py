from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


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
