import urllib.parse
import itertools
import datetime
import pytz
import requests
import lxml.html
from tv_schedule import schedule


def need_channel_code():
    return False

_URL = 'http://www.otr-online.ru'
_SCHED_URL = 'teleprogramma'

_source_tz = pytz.UTC


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url)
    doc = lxml.html.fromstring(resp.content)
    return doc[1][14][4][0][1][0][0]


def _get_id(url):
    i = url.rfind('/') + 1
    j = url.rfind('-', i) + 1
    if j > 0:
        i = j
    return int(url[i: -5])


def _get_descr(url):
    try:
        item = _fetch(url)
    except IndexError:
        pass
    else:
        return '\n'.join(x.text or '' for x in item[1][0].iterchildren('p'))


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        if href and not urllib.parse.urlparse(href).scheme:
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

    slider = _fetch(_SCHED_URL)[3][1]
    for item in itertools.chain(*slider):
        dt = datetime.datetime.utcfromtimestamp(int(item.get('data-time')))
        sched.set_datetime(dt)
        a = item[1][0]
        sched.set_title(a.text)
        descr = descriptions.get(a)
        sched.set_descr(descr)
    return sched.pop()
