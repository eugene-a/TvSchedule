import datetime
import urllib.parse
import itertools
import pytz
import requests
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.tvc.ru/'
_SCHED_URL = '/tvp/index/date/%d-%m-%Y'

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)

_parser = lxml.html.HTMLParser(encoding='utf-8')


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url)
    doc = lxml.html.fromstring(resp.content, parser=_parser)
    page_wrap = doc[1][8]
    return next(itertools.islice(page_wrap.iterchildren('div'), 2, None))


def _get_descr(url):
    content = _fetch(url)
    try:
        info = next(x for x in content.iter('div')
                    if x.get('class') == 'b-brand-episode__info')
        return info[1].text.lstrip()
    except StopIteration:
        pass


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        if href:
            key = int(href[href.rindex('/') + 1:])
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href)
            return descr


def get_schedule(channel, tz):
    if channel != 'ТВ Центр':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)

    descriptions = _Descriptions()

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        for li in _fetch(d.strftime(_SCHED_URL))[0][12]:
            a = li[0]
            t = next(x for x in a.iterchildren('div')
                     if x.get('class') == 'b-schedule__item__title')
            i = a.index(t)
            sched.set_time(a[i + 2].text)
            sched.set_title(t[0].text)
            ds = a[i + 1].text
            descr = (ds + '\n' if ds else '') + (descriptions.get(a) or '')
            if descr:
                sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
