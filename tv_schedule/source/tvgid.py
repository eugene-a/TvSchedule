import datetime
import urllib.parse
import itertools
import pytz
import requests
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return True

channel_code = None

_URL = 'http://tvgid.ua'
_SCHED_URL = '/tv-program/ch/%d%m%Y/id{}/'
_source_tz = pytz.timezone('Europe/Kiev')
_daydelta = datetime.timedelta(1)


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url)
    doc = lxml.html.fromstring(resp.content)
    return doc[1][1][0][0][0][0][0][1][1][1]


def _get_descr(url):
    ncnt = _fetch(url).get_element_by_id('ncnt')
    for br in ncnt.iterdescendants('br'):
        br.tail = '\n' + (br.tail or '')
    return ncnt.text_content()


def _get_id(url):
    i = url.rindex('id') + 2
    return int(url[i: url.index('/', i)])


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        if href is not None:
            key = _get_id(href)
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href)
            return descr


def get_schedule(channel, tz):
    ch_code = channel_code.get(channel)
    if ch_code is None:
        return []

    today = dateutil.tv_date_now(_source_tz, 5)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()
    sched_url = _SCHED_URL.format(ch_code)

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        url = d.strftime(sched_url)
        famediv = _fetch(url).get_element_by_id('famediv')
        table = next(itertools.islice(famediv.itersiblings(), 2, None))

        for row in (x[0][0][0] for x in table[1:]):
            it = row.iterchildren()
            sched.set_time(next(it).text)
            a = next(it)[0]
            sched.set_title(a.text)
            descr = descriptions.get(a)
            if descr:
                sched.set_descr(descr)
        d += _daydelta
    return sched.pop()
