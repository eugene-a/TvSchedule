import datetime
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule


def need_channel_code():
    return False

_URL = 'http://tv.khl.ru/'

_source_tz = pytz.timezone('Europe/Moscow')
_http = httplib2.Http()
_parser = lxml.etree.HTMLParser()


def get_schedule(channel, tz):
    if channel != 'КХЛ ТВ':
        return []

    sched = schedule.Schedule(tz, _source_tz)
    content = _http.request(_URL)[1]
    doc = lxml.etree.fromstring(content, _parser)
    channel = doc[1][6][2][0][2][1]
    for item, progs in zip(channel[2][0], channel[4]):
        d = datetime.datetime.strptime(item[0][0].text, '%a %d.%m.%y')
        sched.set_date(d)
        for prog in progs:
            it = prog.iterchildren()
            sched.set_time(next(it).text)
            sched.set_title(next(it).text)
            try:
                sched.set_descr(next(it).text)
            except StopIteration:
                pass

    return sched.pop()
