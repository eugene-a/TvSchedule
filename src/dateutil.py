from datetime import date, datetime
from env import windows


def _set_month_and_year():
    global _MONTH, _YEAR
 
    today = date.today()
    _MONTH = today.month
    _YEAR = today.year

_MONTH = _YEAR = None
_set_month_and_year()

del _set_month_and_year


def genitive_month(s):
    return s + 'а' if s[-1] == 'т' else s[: -1] + 'я'


def _win2linux_month(month):
    month_map = {
        'Фев': 'Февр.', 'Мар': 'Марта', 'Май': 'Мая',
        'Сен': 'Сент.', 'Ноя': 'Нояб.'
    }

    return month_map.get(month) or month + ('.' if month[0] != 'И' else 'я')


def fromwin(s):
    return s if windows() else s[:2] + '.' + s[2:-3] + _win2linux_month(s[-3:])


def _nominative_month(s):
    s = s[: -1]
    last = s[-1]
    if last != 'т':
        s += ('й' if last == 'а' else 'ь')
    return s


def _fixyear(date):
    mdelta = date.month - _MONTH
    if mdelta < -1:
        date.replace(date.year + 1)
    elif mdelta > 1:
        date.replace(date.year - 1)
    return date

_YEAR_STR = ' ' + str(_YEAR)

def parse_date(s, format):
    if format[-1] == 'B':
        s = _nominative_month(s)
    dt = datetime.strptime(s + _YEAR_STR, format + ' %Y')
    return _fixyear(dt.date())
