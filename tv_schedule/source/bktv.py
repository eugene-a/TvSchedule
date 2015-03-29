import datetime
import pytz
import lxml.etree
from tv_schedule import schedule


def need_channel_code():
    return False

_URL = 'http://www.bk-tv.ru/xml/small.xml'
_source_tz = pytz.timezone('Europe/Moscow')


def get_schedule(channel, tz):
    if channel != 'Бойцовский клуб':
        return []

    sched = schedule.Schedule(tz, _source_tz)

    tree = lxml.etree.parse(_URL)
    for event in tree.getroot()[1:]:
        start = event.get('start')
        dt = datetime.datetime.strptime(start, '%Y%m%d%H%M%S +0000')
        sched.set_datetime(dt)
        title, dot, descr = event[0].text.partition('. ')
        sched.set_title(title)
        sched.set_descr(descr)

    return sched.pop()
