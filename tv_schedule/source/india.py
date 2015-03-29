import datetime
import pytz
import lxml.etree
from tv_schedule import schedule


def need_channel_code():
    return False

_URL = 'http://indiatv.ru/teleprogram/'
_source_tz = pytz.timezone('Europe/Moscow')
_parser = lxml.etree.HTMLParser()


def get_schedule(channel, tz):
    if channel != 'Индия ТВ':
        return []

    sched = schedule.Schedule(tz, _source_tz)

    tree = lxml.etree.parse(_URL, _parser)
    doc = tree.getroot()
    program = doc[1][0][0][3][0][0][1][2]
    for tab in program[4: 11]:
        dt = datetime.datetime.strptime(tab.get('rel'), 'tv_%Y%m%d')
        sched.set_date(dt.date())
        for event in tab[0]:
            it = event.iterchildren()
            sched.set_time(next(it).text)
            span = next(it)
            sched.set_title(span.text.lstrip())
            sched.set_descr(span[0].text)
    return sched.pop()
