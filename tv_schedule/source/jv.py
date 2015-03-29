import pytz
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.jv.ru/live'
_source_tz = pytz.timezone('Europe/Moscow')
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def get_schedule(channel, tz):
    if channel != 'ЖИВИ!':
        return []

    sched = schedule.Schedule(tz, _source_tz)

    tree = lxml.etree.parse(_URL, _parser)
    doc = tree.getroot()
    tabs = doc[2][31][0][0][6]
    for day, tab in zip(tabs[1], tabs[3]):
        d = dateutil.parse_date(day.text.strip() + day[0].text, '%a%d.%m')
        sched.set_date(d)
        for event in (x for x in tab if len(x) > 0):
            it = event.iterchildren()
            sched.set_time(next(it).text)
            sched.set_title(next(it).text.strip())
    return sched.pop()
