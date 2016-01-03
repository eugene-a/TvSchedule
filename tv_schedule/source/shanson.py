import datetime
import pytz
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_YAMAL = 0
_HOTBIRD = 2

_SAT = _YAMAL

_URL = 'http://www.shanson.tv/schedule/'
_FORMAT = 'Программа ШАНСОН ТВ %d %B (%A) %Y года'

_source_tz = pytz.timezone('Europe/Moscow')
_parser = lxml.etree.HTMLParser()


def _nominative_month(s):
    spl = s.split(' (')
    spl[0] = dateutil.nominative_month((spl[0]))
    return ' ('.join(spl)


def get_schedule(channel, tz):
    if channel != 'Шансон ТВ':
        return []

    sched = schedule.Schedule(tz, _source_tz)

    tree = lxml.etree.parse(_URL, _parser)
    doc = tree.getroot()
    table = doc[1][0][0][0][0][3]

    for tr in table[1:3]:
        for day in tr[_SAT][::3]:
            date_str = _nominative_month(day[0].text)
            dt = datetime.datetime.strptime(date_str, _FORMAT)
            sched.set_date(dt.date())
            for row in day.getnext():
                it = row.iterchildren()
                sched.set_time(next(it)[0].text)
                next(it)
                info = next(it)
                title = info.text
                title = title[:-1].rstrip() + title[-1]
                sched.set_title(title)
                if len(info) > 1:
                    descr = info[1].text
                    if descr:
                        sched.set_descr(descr)
    return sched.pop()
