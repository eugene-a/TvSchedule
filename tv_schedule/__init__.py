import locale
from encodings import cp866
from tv_schedule import cp1251ext, env


# dont let the system fall asleep!
def no_idle():
    if env.windows():
        from ctypes import windll
        es_system_required = 0x00000001
        es_continuous = 0x80000000
        windll.kernel32.SetThreadExecutionState(
            es_system_required | es_continuous)


def init():
    loc = env.locale_ru()
    locale.setlocale(locale.LC_CTYPE, loc)
    locale.setlocale(locale.LC_TIME, loc)
    no_idle()

init()
del init

cp1251ext.register()

# print ukrainian 'i' to console as latin 'i'
cp866.encoding_map[ord('і')] = cp866.encoding_map[ord('i')]
