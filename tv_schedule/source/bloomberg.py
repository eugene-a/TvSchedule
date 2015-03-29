import datetime
import pytz
import lxml.etree
from tv_schedule import schedule


def need_channel_code():
    return False

_URL = 'http://www.bloomberg.com/tv/schedule/europe/'
_source_tz = pytz.timezone('CET')
_parser = lxml.etree.HTMLParser()

_month = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]


def _to_month_number(s):
    spl = s.split(None, 1)
    spl[0] = str(_month.index(spl[0]) + 1)
    return ' '.join(spl)


def get_schedule(channel, tz):
    if channel != 'Bloomberg TV':
        return []

    sched = schedule.Schedule(tz, _source_tz)

    tree = lxml.etree.parse(_URL, _parser)
    doc = tree.getroot()
    for tab in doc[1][21][6][0][0][3:]:
        it = tab.iterchildren()
        date = _to_month_number(next(it).text)
        d = datetime.datetime.strptime(date, '%m %d, %Y')
        sched.set_date(d)
        for row in next(it)[0][1:]:
            it = row.iterdescendants()
            sched.set_time(next(it).text)
            next(it)
            sched.set_title(next(it).text.strip())
            sched.set_descr(next(it).text.strip())
    return sched.pop()
