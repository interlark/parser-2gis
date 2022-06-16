<p align="center">
  <a href="#">
    <img alt="Logo" width="128" src="https://user-images.githubusercontent.com/20641837/174094285-6e32eb04-7feb-4a60-bddf-5a0fde5dba4d.png"/>
  </a>
</p>
<h1 align="center">Parser2GIS</h1>

<p align="center">
  <a href="https://github.com/interlark/parser-2gis/actions/workflows/tests.yml"><img src="https://github.com/interlark/parser-2gis/actions/workflows/tests.yml/badge.svg" alt="Tests"/></a>
  <a href="https://pypi.org/project/parser-2gis"><img src="https://badgen.net/pypi/v/parser-2gis" alt="PyPi version"/></a>
  <a href="https://pypi.org/project/parser-2gis"><img src="https://badgen.net/pypi/python/parser-2gis" alt="Supported Python versions"/></a>
  <a href="https://github.com/interlark/parser-2gis/blob/main/LICENSE"><img src="https://badgen.net/pypi/license/parser-2gis" alt="License"/></a>
</p>

**Parser2GIS** - парсер сайта [2GIS](https://2gis.ru/) с помощью браузера [Google Chrome](https://google.com/chrome).

<img alt="Screenshot" src="https://user-images.githubusercontent.com/20641837/174098241-7c0874aa-e70d-4978-86dc-7fd90af44603.png"/>

## ℹ️ Описание
Парсер для автоматического сбора базы адресов и контактов предприятий, которые работают на территории
России 🇷🇺, Казахстана 🇰🇿, Украины 🇺🇦, Беларуси 🇧🇾,
Азербайджана 🇦🇿, Киргизии 🇰🇬, Узбекистана 🇺🇿, Чехии 🇨🇿, Египта 🇪🇬, Италии 🇮🇹, Саудовской Аравии 🇸🇦, Кипра 🇨🇾, Объединенных Арабских Эмиратов 🇦🇪, Чили 🇨🇱, Катара 🇶🇦, Омана 🇴🇲, Бахрейна 🇧🇭.

## 🚀 Установка
> Для работы парсера необходимо установить браузер [Google Chrome](https://google.com/chrome).

### Установка одним файлом

  Скачать [релиз](https://github.com/interlark/parser-2gis/releases/latest).

### Установка из PyPI
  ```bash
  # CLI
  pip install parser-2gis
  # CLI + GUI
  pip install parser-2gis[gui]
  ```
 
### Установка из репозитория
  ```bash
  git clone https://github.com/interlark/parser-2gis
  cd parser-2gis
  
  python -m venv venv
  
  # Windows
  .\venv\Scripts\activate.bat
  # Linux, MacOS
  . venv/bin/activate
  
  # CLI
  pip install .
  # CLI + GUI
  pip install .[gui]
  ```

## 📖 Документация
Описание работы доступно на [вики](https://github.com/interlark/parser-2gis/wiki).
