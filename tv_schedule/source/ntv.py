import datetime
import urllib.parse
import requests
import pytz
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.ntv.ru'
_SCHED_URL = '/rest/currsched.jsp'

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)


_parser = lxml.html.HTMLParser(encoding='cp1251')


def _fetch(url, params=None):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url, params)
    return lxml.html.fromstring(resp.content, parser=_parser)


def _get_descr(url):
    body = _fetch(url)[1]
    bgout = next(x for x in body if x.get('id') == 'bgout')
    try:
        abt = next(x for x in bgout[0][0][0] if x.get('id') == 'abt')
    except StopIteration:
        return ''
    else:
        return abt[1].text_content()


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        try:
            key = href[href.rindex('/', 0, -1) + 1: -1]
        except ValueError:
            return
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
        tbs = _fetch(_SCHED_URL, {'d': d.strftime('%Y%m%d')})
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
