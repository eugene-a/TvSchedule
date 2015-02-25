import datetime
import lxml.etree
import pytz

from tv_schedule import schedule


def need_channel_code():
    return False

_URL = 'http://9tv.co.il/tv-shows/'
_source_tz = pytz.timezone('Israel')
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def get_schedule(channel, tz):
    if channel != '9 Канал Израиль':
        return []

    sched = schedule.Schedule(tz, _source_tz)

    etree = lxml.etree.parse(_URL, _parser)
    content = etree.getroot()[2][8][0][4][0][0][4]
    for tv_program in content[4: 11]:
        date_str = tv_program.get('id')[-8:]
        d = datetime.datetime.strptime(date_str, '%Y%m%d').date()
        sched.set_date(d)
        for li in tv_program[0]:
            span = li[0]
            sched.set_time(span.text)
            sched.set_title(span.tail)
    return sched.pop()
