import urllib.parse
import pytz
import requests
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False


_URL = 'http://oruzhie.tv'
_SCHED_URL = '/programm/'

_source_tz = pytz.timezone('Europe/Moscow')
_parser = lxml.etree.HTMLParser()


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url)
    doc = lxml.etree.fromstring(resp.content, _parser)
    return doc[1][3][1][4][1][1][1]


def _get_descr(url):
    return _fetch(url)[0][2].text or ''


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = int(href.split('/')[2])
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    if channel != 'Оружие':
        return []

    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    for sch in _fetch(_SCHED_URL)[2:]:
        d = dateutil.parse_date(sch[0].text, '%A, %d %B')
        sched.set_date(d)
        for row in sch[1]:
            it = row.iterchildren()
            sched.set_time(next(it)[0].text)
            a = next(it)[0][0][0][0][1]
            sched.set_title(a.text)
            sched.set_descr((descriptions.get(a)))
    return sched.pop()
