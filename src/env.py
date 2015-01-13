from platform import system


def _get_env():
    platform = system()

    if platform == 'Windows':
        def windows():
            return True

        def locale_ru():
            return 'Russian_Russia.1251'

    elif platform == 'Linux':
        def windiws():
            return False

        def locale_ru():
            return 'ru_RU.CP1251'

    else:
        raise Exception(platform + ': unsupported platform')

    return (windows, locale_ru)

windows, locale_ru = _get_env()

del _get_env
