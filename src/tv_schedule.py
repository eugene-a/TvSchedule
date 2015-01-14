from locale import setlocale, LC_CTYPE, LC_TIME
from encodings import cp866

import cp1251m
from env import windows, locale_ru
from schwriter import write_schedule


def no_idle():
    if windows():
        from ctypes import windll
        es_system_required = 0x00000001
        es_continuous = 0x80000000
        windll.kernel32.SetThreadExecutionState(
            es_system_required | es_continuous)


def init():
    locale = locale_ru()
    setlocale(LC_CTYPE, locale)
    setlocale(LC_TIME, locale)
    no_idle()

init()
del init

cp1251m.register()

# print ukrainian 'i' to console as latin 'i'
cp866.encoding_map[ord('і')] = cp866.encoding_map[ord('i')]

write_schedule('tv_schedule.ini')
