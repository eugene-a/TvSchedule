import datetime
import urllib.parse
import httplib2
import pytz
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.ntv.ru'
_URL_PROG = '/rest/currsched.jsp?'

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)


_http = httplib2.Http()
_parser = lxml.html.HTMLParser(encoding='cp1251')


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    return lxml.html.fromstring(content, parser=_parser)


def _get_descr(url):
    doc = _fetch(url)
    cleft = doc[1][21][0][0][1]
    abt = next(x for x in cleft.iterchildren() if x.get('id') == 'abt')
    return abt[1].text_content()


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        path = urllib.parse.urlsplit(href).path
        key = path.split('/')[-2]
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)

        return descr


def get_schedule(channel, tz):
    if channel != 'НТВ':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    descriptions = _Descriptions()

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        query = {'d': d.strftime('%Y%m%d')}
        tbs = _fetch(_URL_PROG + urllib.parse.urlencode(query))
        for dt in tbs[1][::2]:
            dd = dt.getnext()
            if len(dt) > 0:
                dt = dt[0]
            if dd[0].tag == 's':
                dd = dd[0]
            sched.set_time(dt.text)
            a = dd[0]
            sched.set_title(a.text)
            sched.set_descr(descriptions.get(a))
        d += _daydelta
    return sched.pop()
