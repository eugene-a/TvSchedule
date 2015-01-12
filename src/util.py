import re
from platform import system
from locale import setlocale, LC_CTYPE, LC_TIME
from datetime import date
from enum import Enum


class Platform(Enum):
    Windows = 1
    Linux = 2

try:
    PLATFORM = Platform[system()]
except KeyError:
    raise Exception(system() + ': unsupported platform')

MONTH = YEAR = YEAR_STR = None

def init():
    global MONTH, YEAR,  YEAR_STR, TIMEZONE

    today = date.today()

    MONTH = today.month
    YEAR = today.year
    YEAR_STR = ' ' + str(YEAR)

    if PLATFORM is Platform.Windows:
        ru_locale = 'Russian_Russia.1251'
    else:
        ru_locale = 'ru_RU.CP1251'

    setlocale(LC_CTYPE, ru_locale)
    setlocale(LC_TIME, ru_locale)


init()
del init


def add_year(s):
    return s + YEAR_STR


def fixyear(date):
    mdelta = date.month - MONTH
    if mdelta < -1:
        date.replace(date.year + 1)
    elif mdelta > 1:
        date.replace(date.year - 1)
    return date


def get_date(month,  day):
    return fixyear(date(YEAR,  month,  day))


#For strptime.
def nominative_month(s):
    s = s[: -1].lower()
    last = s[-1]
    if last != 'т':
        s += ('й' if last == 'а' else 'ь')
    return s


def genitive_month(s):
    return s + 'а' if s[-1] == 'т' else s[: -1] + 'я'


# ListTV chokes if it encounters a date within text
# This can be avoided by replacing spaces separating day and month
# with something else
def create_date_pattern():
    d = date(1900, 1, 1)
    gm = genitive_month
    pattern = r'(\d{1,2}) +(' + '|'.join(
        (gm(d.replace(month=m).strftime('%B')) for m in range(1, 13))
    ) + ')'
    return re.compile(pattern, re.I | re.U)

DATE_PATTERN = create_date_pattern()

del create_date_pattern


def prepare(s):
    s = s.strip()
    s = re.sub(r'\s+\n', '\n', s)                   # remove trailing spaces
    s = re.sub(r'\n+', '\n', s)                      # remove empty lines
    s = re.sub(r'(\w)\n', r'\1.\n', s)          # end line with a period
    return re.sub(DATE_PATTERN, r'\1-\2', s)  # dash between day and month


def extract_text(elem):
    elem_tail = elem.tail or ''
    return ('\n' if elem.tag == 'br' else elem.text or '') + elem_tail

def no_idle():
    if PLATFORM is Platform.Windows:
        from ctypes import windll
        es_system_required = 0x00000001
        es_continuous = 0x80000000
        windll.kernel32.SetThreadExecutionState(es_system_required | es_continuous)
