import datetime
from tv_schedule import env


# convert abbreviated month
def _win2linux_month(month):
    month_map = {
        'Фев': 'Февр.', 'Мар': 'Марта', 'Май': 'Мая',
        'Сен': 'Сент.', 'Ноя': 'Нояб.'
    }

    return month_map.get(month) or month + ('.' if month[0] != 'И' else 'я')


# s starts with an abbreviated weekday (2 chars)
# and ends with an abbreviated month (3 chars)
if env.windows():
    def fromwin(s):
        return s
else:
    def fromwin(s):
        return s[:2] + '.' + s[2:-3] + _win2linux_month(s[-3:])


# month as an integer and year as a string with a leading space
def _get_month_and_year(d):
    return d.month, ' ' + str(d.year)

_month, _year = _get_month_and_year(datetime.date.today())

del _get_month_and_year


# check if there is a closer date across a year boundary
def _fixyear(d):
    mdelta = d.month - _month
    if mdelta < -6:
        d.replace(d.year + 1)
    elif mdelta > 6:
        d.replace(d.year - 1)
    return d


def genitive_month(s):
    return s + 'а' if s[-1] == 'т' else s[: -1] + 'я'


def nominative_month(s):
    s = s[: -1]
    last = s[-1]
    if last != 'т':
        s += ('й' if last == 'а' else 'ь')
    return s


# parse a date string with no year information
# assuming proximity to the current date
def parse_date(s, format):
    if format[-1] == 'B':
        s = nominative_month(s)
    #  initially assume the current year
    dt = datetime.datetime.strptime(s + _year, format + ' %Y')
    return _fixyear(dt.date())


# TV programs for a day usually begin in the morning
# and end in the  morning of the next day.
def tv_date_now(tz, hours=6, minutes=0):
    now = datetime.datetime.now(tz)
    shift = datetime.timedelta(hours=hours, minutes=minutes)
    return (now - shift).date()
