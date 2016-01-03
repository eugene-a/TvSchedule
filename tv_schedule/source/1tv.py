import datetime
import urllib.parse
import itertools
import pytz
import requests
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://1tv.com.ua'
_SCHED_URL = 'schedule/load/week2day{}'
_daydelta = datetime.timedelta(1)
_source_tz = pytz.timezone('Europe/Kiev')
_parser = lxml.etree.HTMLParser(encoding='utf-8')


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url)
    return lxml.etree.fromstring(resp.content, _parser)


def _get_descr(url):
    container = _fetch(url)[1][14]
    if len(container) > 5:
        cut = container[4][0][11][1][0]
        return '\n'.join(x.text or ''
                         for x in cut.iterdescendants() if len(x) == 0)


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        islash = href.rindex('/')
        if islash > 0:
            key = href[islash + 1:]
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href)
            return descr


def get_schedule(channel, tz):
    if channel != 'Перший Національний / Ера':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.isoweekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    d = today
    for i in range(weekday_now, 8):
        sched.set_date(d)
        doc = _fetch(_SCHED_URL.format(i))
        divs = doc[0][0][2][0].iterchildren('div')
        for time in itertools.islice(divs, 0, None, 3):
            sched.set_time(time.text)
            span = next(x for x in time.getnext() if x.get('class') is None)
            if len(span) < 1:
                sched.set_title(span.text)
            else:
                a = span[0]
                sched.set_title(a.text)
                descr = descriptions.get(a)
                if descr:
                    sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
