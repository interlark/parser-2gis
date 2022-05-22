# Parser2GIS
[![Tests](https://github.com/interlark/parser-2gis/actions/workflows/tests.yml/badge.svg)](https://github.com/interlark/parser-2gis/actions/workflows/tests.yml)
[![PyPi version](https://badgen.net/pypi/v/parser-2gis)](https://pypi.org/project/parser-2gis)
[![Supported Python versions](https://badgen.net/pypi/python/parser-2gis)](https://pypi.org/project/parser-2gis)
[![PyPi license](https://badgen.net/pypi/license/parser-2gis)](https://pypi.org/project/parser-2gis)

Парсер сайта [2GIS](https://2gis.ru/) с помощью браузера [Google Chrome](https://google.com/chrome).

![Screenshot](https://raw.githubusercontent.com/interlark/parser-2gis/main/assets/screenshots/main_and_settings.png)

## Описание
Парсер для автоматического сбора базы адресов и контактов предприятий, которые работают на территории
России 🇷🇺, Казахстана 🇰🇿, Украины 🇺🇦, Беларуси 🇧🇾,
Азербайджана 🇦🇿, Киргизии 🇰🇬, Узбекистана 🇺🇿, Чехии 🇨🇿, Египта 🇪🇬, Италии 🇮🇹, Саудовской Аравии 🇸🇦, Кипра 🇨🇾, Объединенных Арабских Эмиратов 🇦🇪, Чили 🇨🇱, Катара 🇶🇦, Омана 🇴🇲, Бахрейна 🇧🇭.

## Установка
> Для работы парсера необходимо установить браузер [Google Chrome](https://google.com/chrome).

- Скачать [релиз](https://github.com/interlark/parser-2gis/releases/latest) и запустить.

- Установка из PyPI:
```bash
# CLI
pip install parser-2gis
# CLI + GUI
pip install parser-2gis[gui]
```

- Установка из репозитория:
```bash
git clone https://github.com/interlark/parser-2gis
cd parser-2gis

python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux, MacOS
. venv/bin/active.bat

# CLI
pip install .
# CLI + GUI
pip install .[gui]
```

## Документация
Описание работы доступно на [вики](https://github.com/interlark/parser-2gis/wiki).
