from __future__ import annotations

import functools
import sys
import time
import warnings
from typing import Any, Callable

from pydantic import ValidationError

try:
    import PySimpleGUI
    del PySimpleGUI
    GUI_ENABLED = True
except ImportError as e:
    if e.name != 'PySimpleGUI':
        # GUI was installed, but failed to load
        # due to tkinter missing or other dependencies.
        warnings.warn('Failed to load GUI: %s' % e.msg)
    GUI_ENABLED = False


def running_linux() -> bool:
    """Determine if current OS is Linux-based."""
    return sys.platform.startswith('linux')


def running_windows() -> bool:
    """Determine if current OS is Windows."""
    return sys.platform.startswith('win')


def running_mac() -> bool:
    """Determine if current OS is MacOS."""
    return sys.platform.startswith('darwin')


def wait_until_finished(timeout: int | None = None,
                        finished: Callable[[Any], bool] = lambda x: bool(x),
                        throw_exception: bool = True,
                        poll_interval: float = 0.1) -> Callable[..., Callable[..., Any]]:
    """Decorator that polls wrapped function until time is out or `finished`
    predicate returns `True`.

    Args:
        timeout: Max time to wait.
        finished: Predicate for successed result of decorated function.
        throw_exception: Whether to throw `TimeoutError`.
        poll_interval: Poll interval for result of decorated function.
    """
    def outer(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def inner(*args, timeout=timeout, finished=finished,
                  throw_exception=throw_exception,
                  poll_interval=poll_interval, **kwargs):
            call_time = time.time()
            while True:
                ret = func(*args, **kwargs)
                if not timeout or finished(ret):
                    return ret

                if time.time() - call_time > timeout:
                    if throw_exception:
                        raise TimeoutError(func)
                    return ret

                time.sleep(poll_interval)
        return inner
    return outer


def report_from_validation_error(ex: ValidationError,
                                 d: dict | None = None) -> dict:
    """Generate validation error report
    for `BaseModel` out of `ValidationError`.

    Note:
        It's convinient to use when you try to instantiate
        model with predefined dictionary. For example:

        class TestModel(BaseModel):
            test_int: int

        try:
            d = {'test_int': '_12'}
            m = TestModel(**d)
        except ValidationError as ex:
            print(report_from_validation_error(ex, d))

    Args:
        d: Arguments dictionary.
        ex: Thrown Pydantic ValidationError.

    Returns:
        Dictionary with validation error information.
        {
            'full_path_of_invalid_attribute': {
                'invalid_value': ...,
                'error_message': ...,
            },
            ...
        }
    """
    values = {}
    for error in ex.errors():
        msg = error['msg']
        loc = error['loc']
        attribute_path = '.'.join([str(location) for location in loc])

        if d:
            value = d
            for field in loc:
                if field == '__root__':
                    break
                value = value[field]

            values[attribute_path] = {
                'invalid_value': value,
                'error_message': msg,
            }
        else:
            values[attribute_path] = {
                'error_message': msg,
            }

    return values


def unwrap_dot_dict(d: dict) -> dict:
    """Unwrap flat dictionary with keys represented
    by dot-concatenated path to their values.

    Example:
        Input:
            {
                'full.path.filedname': 'value1',
                'another.fieldname': 'value2',
            }

        Output:
            {
                'full': {
                    'path': {
                        'filedname': 'value1',
                    },
                },
                'another': {
                    'fieldname': 'value2',
                },
            }
    """
    output: dict = {}
    for key, value in d.items():
        path = key.split('.')
        target = functools.reduce(lambda d, k: d.setdefault(k, {}), path[:-1], output)
        target[path[-1]] = value
    return output


def floor_to_hundreds(arg: int | float) -> int:
    """Round number down to the nearest hundred."""
    return int(arg // 100 * 100)
