import datetime
import collections
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_source_tz = pytz.utc
_URL = 'http://www.tv21.lv/ru/program/%Y/%m/%d'
_daydelta = datetime.timedelta(1)
_parser = lxml.etree.HTMLParser()
_http = httplib2.Http()


_Event = collections.namedtuple('_Event', 'title times descr')


def _extract(movie):
    title = movie[0][-1].tail.strip()
    body = movie[1]
    times = [x.text for x in body[1]]
    descr = body[2].text
    return _Event(title, times, descr)


def get_schedule(channel, tz):
    if channel != 'TV XXI':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        content = _http.request(d.strftime(_URL))[1]
        doc = lxml.etree.fromstring(content, _parser)
        scroll = doc[1][1][1][2][1][0]
        events = [_extract(x) for x in scroll]
        for j in range(3):
            for ev in events:
                sched.set_time(ev.times[j])
                sched.set_title(ev.title)
                sched.set_descr(ev.descr)
        d += _daydelta
    return sched.pop()
