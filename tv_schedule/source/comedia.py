import datetime
import urllib.parse
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_source_tz = pytz.timezone('Europe/Moscow')
_URL = 'http://www.comediatv.ru'
_SCHED_URL = '/teleprogram/'
_http = httplib2.Http()


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.html.fromstring(content)
    return doc[1][0][0][2][0][0][0][0][1][0]


def _get_descr(url):
    text = _fetch(url)
    return '\n'.join(x.text or '' for x in text)


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = int(href[href.rindex('/', 0, -1) + 1: -1])
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    if channel != 'Комедия ТВ':
        return []

    descriptions = _Descriptions()

    sched = schedule.Schedule(tz, _source_tz)
    for tv in _fetch(_SCHED_URL)[1][4: -1]:
        d = datetime.datetime.strptime(tv.get('rel'), 'tv_%Y%m%d')
        sched.set_date(d)
        for li in tv[0]:
            sched.set_time(li[0].text)
            span = li[1]
            if len(span) == 1:
                title = span.text.lstrip()
                descr = span[0].text
            else:
                a = next(span.iterchildren('a', reversed=True))
                title = a.text
                descr = descriptions.get(a)
            sched.set_title(title)
            sched.set_descr(descr)
    return sched.pop()
