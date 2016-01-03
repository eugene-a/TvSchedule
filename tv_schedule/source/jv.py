import datetime
import pytz
import lxml.etree
from tv_schedule import schedule


def need_channel_code():
    return False

_URL = 'http://www.jv.ru/live'
_source_tz = pytz.UTC
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def get_schedule(channel, tz):
    if channel != 'ЖИВИ!':
        return []

    sched = schedule.Schedule(tz, _source_tz)

    tree = lxml.etree.parse(_URL, _parser)
    doc = tree.getroot()
    tabs = doc[2][32][0][0][6][3]
    for tab in tabs:
        for event in (x for x in tab if len(x) > 0):
            name = event[1]
            dt = datetime.datetime.utcfromtimestamp(int(name.get('data-time')))
            sched.set_datetime(dt)
            it = name.iterchildren(reversed=True)
            descr = next(it).text
            try:
                title = next(it).text
            except StopIteration:
                sched.set_title(descr)
            else:
                sched.set_title(title)
                sched.set_descr(descr)

    return sched.pop()
