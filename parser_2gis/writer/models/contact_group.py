from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from .schedule import Schedule


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
