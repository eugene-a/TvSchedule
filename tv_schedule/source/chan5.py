import datetime
import urllib.parse
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.5-tv.ru/schedule/?'

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)

_http = httplib2.Http()


def _fetch(url):
    content = _http.request(url)[1]
    doc = lxml.html.fromstring(content)
    wrapper = doc[1][0]
    if len(wrapper) > 2:
        return wrapper[2][0][0]


def _get_text(elem):
    return '\n'.join(x.text_content() for x in elem if x.get('class') is None)


def _get_descr(url):
    doc = _fetch(url)
    if doc is not None:
        det = doc[1]
        if det.tag == 'div':
            return _get_text(det[0][1]) + _get_text(det[1])
    return ''


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        if a.tag == 'a':
            href = a.get('href')
            key = int(href[href.rindex('/', 0, -1) + 1: -1])
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href)
            return descr


def get_schedule(channel, tz):
    if channel != 'Пятый канал':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        query = {'date': d.strftime('%Y-%m-%d')}
        url = _URL + urllib.parse.urlencode(query)
        for li in _fetch(url)[3][0]:
            sched.set_time(li[0].text)
            a = li[1]
            if a.tag == 'a':
                sched.set_title(a.text)
                descr = descriptions.get(a)
                if descr:
                    sched.set_descr(descr)
            elif len(a) == 0:
                sched.set_title(a.text)
            else:
                sched.set_title(a[0].text)
        d += _daydelta
    return sched.pop()
