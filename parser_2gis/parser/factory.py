import re

from .parsers import InBuildingParser, MainParser


def get_parser(url, chrome_options, parser_options):
    """Parser factory function.

    Args:
        url: 2GIS URLs with items to be collected.
        chrome_options: Chrome options.
        parser_options: Parser options.

    Returns:
        Parser instance.
    """
    for parser in (InBuildingParser, MainParser):
        if re.match(parser.url_pattern(), url):
            return parser(url, chrome_options, parser_options)

    # Default fallback
    return MainParser(url, chrome_options, parser_options)
