import datetime
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.moya-planeta.ru/program/date/%d-%m-%Y/'

_http = httplib2.Http()
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)

_parser = lxml.etree.HTMLParser()


def _fetch(url):
    content = _http.request(url)[1]
    doc = lxml.etree.fromstring(content, _parser)
    table = doc[1][0][0][1][0]
    return table[0][0][2] if table.tag == 'table' else []


def get_schedule(channel, tz):
    if channel != 'Моя планета':
        return []

    today = dateutil.tv_date_now(_source_tz, 0)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        for ev in _fetch(d.strftime(_URL))[1:]:
            sched.set_time(ev[0].text)
            sched.set_title(ev[1][0].text)
            sched.set_descr(ev[3].text)
        d += _daydelta
    return sched.pop()
