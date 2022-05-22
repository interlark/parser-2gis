from pychrome.exceptions import UserAbortException as ChromeUserAbortException
from pychrome.exceptions import RuntimeException as ChromeRuntimeException


class ChromeException(Exception):
    pass


class ChromePathNotFound(ChromeException):
    def __init__(self, msg='Chrome браузер не найден', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
