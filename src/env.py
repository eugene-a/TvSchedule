from platform import system
from enum import Enum


class Platform(Enum):
    Windows = 1
    Linux = 2


def _set_platform():
    platform = system()
    try:
        return Platform[platform]
    except KeyError:
        raise Exception(platform + ': unsupported platform')

_PLATFORM = _set_platform()
del _set_platform


def windows():
    return _PLATFORM is Platform.Windows


def linux():
    return _PLATFORM is Platform.Linux


def locale_ru():
    if windows():
        return 'Russian_Russia.1251'
    else:
        return 'ru_RU.CP1251'
