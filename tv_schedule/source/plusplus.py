import datetime
import urllib.parse
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://plus-plus.tv/dyvys/rozklad/?day=23&month=03&year=2015'
_SCHED_URL = '/uk/tv/%Y/%m/%d'
_source_tz = pytz.timezone('Europe/Kiev')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
_parser = lxml.etree.HTMLParser()


def _fetch(url):
    content = _http.request(url)[1]
    doc = lxml.etree.fromstring(content, _parser)
    return doc[1][1][1][0][1][0][2]


def _get_descr(url):
    return '/n'.join(x.text or '' for x in _fetch(url)[2][2])


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
        query = {'day': d.day, 'month': d.month, 'year': d.year}
        url = _URL + urllib.parse.urlencode(query)
        i = 0
        for list in _fetch(url)[4]:
            i = 1 - i
            for a in (x[i][0] for x in list if len(x[i]) > 0):
                it = a.iterchildren()
                sched.set_time(next(it).text)
                sched.set_title(next(it).text)
                sched.set_descr(descriptions.get(a))
        d += _daydelta
    return sched.pop()
