import datetime
import urllib.parse
import pytz
import requests
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://www.gulli.ru'
_SCHED_URL = '/schedule/'
_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)
_parser = lxml.etree.HTMLParser()


def _fetch(url, params=None):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url, params)
    doc = lxml.etree.fromstring(resp.content, _parser)
    inner = doc[1][0][6][0][0][2]
    if len(inner) > 0:
        return inner[0][2]


def _get_descr(url):
    descr = _fetch(url)
    return descr[1].text if descr is not None else ''


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        if not urllib.parse.urlparse(href).scheme:
            key = href[href.rindex('/') + 1:]
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href)
            return descr


def get_schedule(channel, tz):
    if channel != 'Gulli':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()
    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)

        for item in _fetch(_SCHED_URL, {'date': d.strftime('%Y-$m-%d')}):
            it = item.iterchildren()
            next(it)
            sched.set_time(next(it).text)
            a = next(it)[0]
            sched.set_title(a.text.strip())
            sched.set_descr(descriptions.get(a))
        d += _daydelta
    return sched.pop()
