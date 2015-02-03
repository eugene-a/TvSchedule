import platform


def _get_env():
    system = platform.system()

    if system == 'Windows':
        def windows():
            return True

        def locale_ru():
            return 'Russian_Russia.1251'

    elif system == 'Linux':
        def windows():
            return False

        def locale_ru():
            return 'ru_RU.CP1251'

    else:
        raise Exception(system + ': unsupported platform')

    return windows, locale_ru

windows, locale_ru = _get_env()

del _get_env
