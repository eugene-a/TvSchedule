import datetime
import urllib.parse
import pytz
import requests
import lxml.html
from tv_schedule import schedule


def need_channel_code():
    return False

_URL = 'http://www.boets.ru'
_SCHED_URL = '/teleprogram'
_source_tz = pytz.timezone('Europe/Moscow')
_parser = lxml.html.HTMLParser(encoding='utf-8')


def _fetch(url):
    resp = requests.get(url)
    doc = lxml.html.fromstring(resp.content, parser=_parser)
    return doc[1][3][0][1][0][2][0]


def _get_descr(url):
    return '\n'.join(x.text_content() for x in _fetch(url)[0][2: -1])


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = int(href[href.rindex('/') + 1:])
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    if channel != 'Боец':
        return []

    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    url = urllib.parse.urljoin(_URL, _SCHED_URL)
    zoo = _fetch(url)
    for tab in zoo[1][4: -1]:
        d = datetime.datetime.strptime(tab.get('data-day'), 'tv_%Y%m%d')
        sched.set_date(d)
        for item in tab[0]:
            it = item.iterchildren()
            sched.set_time(next(it).text)
            span = next(it)
            if len(span) < 2:
                sched.set_title(span.text.lstrip())
            else:
                a = next(span.iterchildren('a', reversed=True))
                sched.set_title(a.text)
                sched.set_descr(descriptions.get(a))
    return sched.pop()
