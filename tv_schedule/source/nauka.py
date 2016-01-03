import datetime
import pytz
import lxml.etree
from tv_schedule import schedule


def need_channel_code():
    return False

_URL = 'http://www.naukatv.ru/xml/small.xml'
_source_tz = pytz.timezone('Europe/Moscow')


def get_schedule(channel, tz):
    if channel != 'Наука 2.0':
        return []

    sched = schedule.Schedule(tz, _source_tz)

    tree = lxml.etree.parse(_URL)
    for event in tree.getroot():
        it = event.iterchildren()
        dt = datetime.datetime.strptime(next(it).text, '%Y-%m-%d %H:%M:%S')
        sched.set_datetime(dt)
        sched.set_title(next(it).text)
        sched.set_descr(next(it).text)

    return sched.pop()
