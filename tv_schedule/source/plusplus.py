import datetime
import pytz
import requests
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://plus-plus.tv/dyvys/rozklad/'
_source_tz = pytz.timezone('Europe/Kiev')
_daydelta = datetime.timedelta(1)
_parser = lxml.etree.HTMLParser()


def _fetch(url, params=None):
    resp = requests.get(url, params)
    doc = lxml.etree.fromstring(resp.content, _parser)
    return doc[1][2][1][0][1][0][2]


def _get_descr(url):
    return '\n'.join(x.text or '' for x in _fetch(url)[2][2])


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        if href:
            key = int(href[href.rindex('-') + 1: -5])
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href)
            return descr


def get_schedule(channel, tz):
    if channel != 'ПлюсПлюс':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        params = {'day': d.day, 'month': d.month, 'year': d.year}
        i = 0
        for lst in _fetch(_URL, params)[4]:
            i = 1 - i
            for a in (x[i][0] for x in lst if len(x[i]) > 0):
                it = a.iterchildren()
                sched.set_time(next(it).text)
                sched.set_title(next(it).text)
                sched.set_descr(descriptions.get(a))
        d += _daydelta
    return sched.pop()
