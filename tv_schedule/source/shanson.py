import datetime
import pytz
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

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

    tree = lxml.etree.parse(_URL, _parser)
    doc = tree.getroot()
    left = doc[1][0][0][0][0]
    hr = next(x for x in left if x.tag == 'hr')
    del left[left.index(hr)]
    hr = next(x for x in left if x.tag == 'hr')

    sched = schedule.Schedule(tz, _source_tz)

    for day in left[3: left.index(hr): 3]:
        date_str = _nominative_month(day[0].text)
        dt = datetime.datetime.strptime(date_str, _FORMAT)
        sched.set_date(dt.date())
        for row in day.getnext():
            it = row.iterchildren()
            sched.set_time(next(it)[0].text)
            next(it)
            info = next(it)
            sched.set_title(info.text)
            descr = info[1].text.strip()
            if descr:
                sched.set_descr(info[1].text)
    return sched.pop()
