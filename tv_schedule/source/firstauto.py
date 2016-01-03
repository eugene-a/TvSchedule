import urllib.parse
import pytz
import requests
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.1auto.tv'
_SCHED_URL = '/schedule'
_source_tz = pytz.timezone('Europe/Kiev')


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url)
    doc = lxml.html.fromstring(resp.content)
    return doc[1][3][4][0][0][1]


def _get_descr(url):
    return _fetch(url)[2].text_content()


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = href[href.rindex('/') + 1: -5]
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    if channel != 'Перший автомобільний':
        return []

    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    days = _fetch(_SCHED_URL)
    for day, table in zip(days, days.getnext()):
        d = dateutil.parse_date(day[0].text + day[1].text, '%a%d %B')
        sched.set_date(d)
        for row in (x for x in table if len(x) > 1):
            it = row.iterchildren()
            sched.set_time(next(it).text)
            inner = next(it)[0]
            if len(inner) == 0:
                sched.set_title(inner.text)
            else:
                a = inner[0]
                sched.set_title(a.text)
                sched.set_descr
                sched.set_descr(descriptions.get(a))
    return sched.pop()
