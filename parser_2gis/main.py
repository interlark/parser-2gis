from __future__ import annotations

import argparse
from typing import Any, Tuple

import pydantic

from .common import GUI_ENABLED, report_from_validation_error, unwrap_dot_dict
from .config import Configuration
from .runner import run_cli, run_gui
from .version import version


class ArgumentHelpFormatter(argparse.HelpFormatter):
    """Help message formatter which adds default values to argument help."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._default_config = Configuration().dict()

    def _get_default_value(self, dest: str) -> Any:
        if dest == 'version':
            return argparse.SUPPRESS

        fileds = dest.split('.')
        value = self._default_config
        try:
            for field in fileds:
                value = value[field]
            return value
        except KeyError:
            return argparse.SUPPRESS

    def _get_help_string(self, action: argparse.Action) -> str | None:
        help_string = action.help
        if help_string:
            default_value = self._get_default_value(action.dest)
            if default_value != argparse.SUPPRESS:
                if isinstance(default_value, bool):
                    default_value = 'yes' if default_value else 'no'
                help_string += f' (по умолчанию: {default_value})'
        return help_string


def patch_argparse_translations() -> None:
    """Patch argparse's `gettext` and make it
    translate some strings into russian."""

    custom_translations = {
        'usage: ': 'Использование: ',
        'one of the arguments %s is required': 'один из аргументов %s обязателен',
        'unrecognized arguments: %s': 'нераспознанные аргументы: %s',
        'the following arguments are required: %s': 'следующие аргументы обязательны: %s',
        '%(prog)s: error: %(message)s\n': '%(prog)s: ошибка: %(message)s\n',
        'invalid choice: %(value)r (choose from %(choices)s)': 'неверная опция: %(value)r (выберите одну из %(choices)s)'
    }

    orig_gettext = argparse._  # type: ignore[attr-defined]

    def gettext(message: str) -> str:
        if message in custom_translations:
            return custom_translations[message]
        return orig_gettext(message)

    argparse._ = gettext  # type: ignore[attr-defined]

    # Also replace hardcoded string `argument` in ArgumentError class
    # (patch tested in Python 3.7, 3.8, 3.9, 3.10)
    # This bug was fixed only on 6 May 2022 https://github.com/python/cpython/pull/17169
    def argument_error__str__(self: argparse.ArgumentError) -> str:
        if self.argument_name is None:
            format = '%(message)s'
        else:
            format = 'аргумент %(argument_name)s: %(message)s'
        return format % dict(message=self.message,
                             argument_name=self.argument_name)

    argparse.ArgumentError.__str__ = argument_error__str__  # type: ignore


def parse_arguments() -> Tuple[argparse.Namespace, Configuration]:
    """Parse arguments depending on whether we got GUI support or not.

    Returns:
        Tuple of Command line arguments and Configuration.
    """
    patch_argparse_translations()  # Patch Russian translations
    arg_parser = argparse.ArgumentParser('Parser2GIS', description='Парсер данных сайта 2GIS', add_help=False,
                                         formatter_class=ArgumentHelpFormatter, argument_default=argparse.SUPPRESS)

    if GUI_ENABLED:
        main_parser_name = 'Основные аргументы'
        main_parser_required = False
    else:
        main_parser_name = 'Обязательные аргументы'
        main_parser_required = True

    main_parser = arg_parser.add_argument_group(main_parser_name)
    main_parser.add_argument('-i', '--url', nargs='+', default=None, required=main_parser_required, help='URL с выдачей')
    main_parser.add_argument('-o', '--output-path', metavar='PATH', default=None, required=main_parser_required, help='Путь до результирующего файла')
    main_parser.add_argument('-f', '--format', metavar='{csv,json}', choices=['csv', 'json'], default=None, required=main_parser_required, help='Формат результирующего файла')

    browser_parser = arg_parser.add_argument_group('Аргументы браузера')
    browser_parser.add_argument('--chrome.binary_path', metavar='PATH', help='Путь до исполняемого файла браузера. Если не указан, то определяется автоматически')
    browser_parser.add_argument('--chrome.disable-images', metavar='{yes,no}', help='Отключить изображения в браузере')
    browser_parser.add_argument('--chrome.headless', metavar='{yes,no}', help='Скрыть браузер')
    browser_parser.add_argument('--chrome.silent-browser', metavar='{yes,no}', help='Отключить отладочную информацию браузера')
    browser_parser.add_argument('--chrome.start-maximized', metavar='{yes,no}', help='Запустить окно браузера развёрнутым')
    browser_parser.add_argument('--chrome.memory-limit', metavar='{4096,5120,...}', help='Лимит оперативной памяти браузера (мегабайт)')

    csv_parser = arg_parser.add_argument_group('Аргументы CSV')
    csv_parser.add_argument('--writer.csv.add-rubrics', metavar='{yes,no}', help='Добавить колонку "Рубрики"')
    csv_parser.add_argument('--writer.csv.add-comments', metavar='{yes,no}', help='Добавлять комментарии к ячейкам Телефон, E-Mail, и т.д.')
    csv_parser.add_argument('--writer.csv.columns-per-entity', metavar='{1,2,3,...}', help='Количество колонок для результата с несколькими возможными значениями: Телефон_1, Телефон_2, и т.д.')
    csv_parser.add_argument('--writer.csv.remove-empty-columns', metavar='{yes,no}', help='Удалить пустые колонки по завершению работы парсера')
    csv_parser.add_argument('--writer.csv.remove-duplicates', metavar='{yes,no}', help='Удалить повторяющиеся записи по завершению работы парсера')
    csv_parser.add_argument('--writer.csv.join_char', metavar='{; ,% ,...}', help='Разделитель для комплексных значений ячеек Рубрики, Часы работы')

    p_parser = arg_parser.add_argument_group('Аргументы парсера')
    p_parser.add_argument('--parser.use-gc', metavar='{yes,no}', help='Включить сборщик мусора - сдерживает быстрое заполнение RAM, уменьшает скорость парсинга')
    p_parser.add_argument('--parser.gc-pages-interval', metavar='{5,10,...}', help='Запуск сборщика мусора каждую N-ую страницу результатов (если сборщик включен)')
    p_parser.add_argument('--parser.max-records', metavar='{1000,2000,...}', help='Максимальное количество спарсенных записей с одного URL')
    p_parser.add_argument('--parser.skip-404-response', metavar='{yes,no}', help='Пропускать ссылки вернувшие сообщение "Точных совпадений нет / Не найдено"')
    p_parser.add_argument('--parser.delay_between_clicks', metavar='{0,100,...}', help='Задержка между кликами по записям (миллисекунд)')

    other_parser = arg_parser.add_argument_group('Прочие аргументы')
    other_parser.add_argument('--writer.verbose', metavar='{yes,no}', help='Отображать наименования позиций во время парсинга')
    other_parser.add_argument('--writer.encoding', metavar='{utf8,1251,...}', help='Кодировка результирующего файла')

    rest_parser = arg_parser.add_argument_group('Служебные аргументы')
    rest_parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {version}', help='Показать версию программы и выйти')
    rest_parser.add_argument('-h', '--help', action='help', help='Показать эту справку и выйти')

    args = arg_parser.parse_args()
    config_args = unwrap_dot_dict(vars(args))

    try:
        # Initialize config with command line arguments
        config = Configuration(**config_args)
    except pydantic.ValidationError as e:
        errors = []
        errors_report = report_from_validation_error(e, config_args)
        for path, description in errors_report.items():
            arg = description['invalid_value']
            error_msg = description['error_message']
            errors.append(f'aргумент --{path} {arg} ({error_msg})')

        arg_parser.error(', '.join(errors))

    return args, config


def main() -> None:
    """Entry point."""
    # Parse command line arguments
    args, command_line_config = parse_arguments()

    # Run CLI if we specified all required args, otherwise run GUI.
    if args.url is None or args.output_path is None or args.format is None:
        # Load user config and merge it with one created by command line arguments.
        user_config = Configuration.load_config(auto_create=True)
        user_config.merge_with(command_line_config)

        run_gui(args.url, args.output_path, args.format, user_config)
    else:
        run_cli(args.url, args.output_path, args.format, command_line_config)
