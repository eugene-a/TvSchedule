from datetime import date, datetime
from env import windows


def genitive_month(s):
    return s + 'а' if s[-1] == 'т' else s[: -1] + 'я'


# convert abbreviated month
def _win2linux_month(month):
    month_map = {
        'Фев': 'Февр.', 'Мар': 'Марта', 'Май': 'Мая',
        'Сен': 'Сент.', 'Ноя': 'Нояб.'
    }

    return month_map.get(month) or month + ('.' if month[0] != 'И' else 'я')


# s starts with an abbreviated weekday (2 chars)
# and ends with an abbreviated month (3 chars)
if windows():
    def fromwin(s):
        return s
else:
    def fromwin(s):
        return s[:2] + '.' + s[2:-3] + _win2linux_month(s[-3:])


def _nominative_month(s):
    s = s[: -1]
    last = s[-1]
    if last != 'т':
        s += ('й' if last == 'а' else 'ь')
    return s


# month as an integer and year as a string with a leading space
def _get_month_and_year(d):
    return (d.month, ' ' + str(d.year))

_MONTH, _YEAR = _get_month_and_year(date.today())

del _get_month_and_year


# check if there is a closer date across a year boundary
def _fixyear(date):
    mdelta = date.month - _MONTH
    if mdelta < -6:
        date.replace(date.year + 1)
    elif mdelta > 6:
        date.replace(date.year - 1)
    return date


# parse a date string with no year information
# assuming proximity to the current date
def parse_date(s, format):
    if format[-1] == 'B':
        s = _nominative_month(s)
    #  initially assume the current year
    dt = datetime.strptime(s + _YEAR, format + ' %Y')
    return _fixyear(dt.date())
