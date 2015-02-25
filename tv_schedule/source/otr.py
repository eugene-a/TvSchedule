import urllib.parse
import operator
import functools
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.otr-online.ru'
_PROG_URL = 'teleprogramma'

_source_tz = pytz.timezone('Europe/Moscow')

_http = httplib2.Http()


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.html.fromstring(content)
    container = next(x for x in doc[1] if x.get('class') == 'conteiner')
    return container[9]


def _get_id(url):
    i = url.rfind('/') + 1
    j = url.rfind('-', i) + 1
    if j > 0:
        i = j
    return int(url[i: -5])


def _get_descr(url):
    bb_none = _fetch(url)[4][0]
    div = next(
        (
            x for x in bb_none
            if len(x) > 0 and x[0].get('class') == 'ProgrammMainDiv'
        ),
        None
        )
    if div is not None:
        return functools.reduce(
            operator.add,
            (x.text or '' for x in div[1].iterchildren('p')),
            ''
        )


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        if href:
            key = _get_id(href)
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href) or ''
            return descr


def get_schedule(channel, tz):
    if channel != 'ОТР':
        return []

    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    for tab in _fetch(_PROG_URL)[2:9]:
        d = dateutil.parse_date(tab.get('id'), 'tab_%d_%m')
        sched.set_date(d)

        for tele in tab:
            a = tele[0]
            span = a[0][0]
            sched.set_time(span.text)
            sched.set_title(span.tail.rstrip())
            descr = descriptions.get(a)
            if descr:
                sched.set_descr(descr)
    return sched.pop()
