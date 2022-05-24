from __future__ import annotations

import base64
import functools
import os
import pathlib

from .common import running_mac, running_windows


def data_path() -> pathlib.Path:
    """Get package's data path."""
    if '_MEIPASS2' in os.environ:
        here = os.environ['_MEIPASS2']
    else:
        here = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(here, 'data')
    return pathlib.Path(path)


def user_path(is_config: bool = True) -> pathlib.Path:
    """Get user path depending on running OS.

    Note:
        Possible path location depending on running OS:
        * Unix: ~/.config/parser-2gis or ~/.local/share/parser-2gis (depends on `is_config` flag)
        * Mac: ~/Library/Application Support/parser-2gis/
        * Win: C:\\Users\\%USERPROFILE%\\AppData\\Local\\parser-2gis
    """
    if running_windows():
        import ctypes

        CSIDL_LOCAL_APPDATA = 28
        buf = ctypes.create_unicode_buffer(1024)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_LOCAL_APPDATA, None, 0, buf)  # type: ignore
        path = buf.value
    elif running_mac():
        path = os.path.expanduser('~/Library/Application Support')
    else:
        if is_config:
            path = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        else:
            path = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))

    path = os.path.join(path, 'parser-2gis')
    return pathlib.Path(path)


@functools.lru_cache()
def image_path(basename: str, ext: str | None = None) -> str:
    """Get image `basename`.`ext`.
    Extension is ignored if `ext` set to `None`.

    Args:
        basename: Image basename.
        ext: Image extension.

    Returns:
        Image path.
    """
    images_dir = data_path() / 'images'
    for img_name in os.listdir(images_dir):
        img_basename, img_ext = os.path.splitext(img_name)
        if img_basename == basename and (ext is None or img_ext == f'.{ext}'):
            return os.path.abspath(images_dir / img_name)

    raise FileNotFoundError(f'Изображение {basename} не найдено')


@functools.lru_cache()
def image_data(basename: str, ext: str | None = None) -> bytes:
    """Get image data `basename`.`ext`.
    Extension is ignored if `ext` set to `None`.

    Args:
        basename: Image basename.
        ext: Image extension.

    Returns:
        Image data.
    """
    with open(image_path(basename, ext), 'rb') as f_img:
        return base64.b64encode(f_img.read())
