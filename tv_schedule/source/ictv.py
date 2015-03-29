import datetime
import json
import urllib.parse
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://ictv.ua'
_SCHED_URL = '/ru/index/programs/theme/0/t/1/date/%Y-%m-%d'
_source_tz = pytz.timezone('Europe/Kiev')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
_parser = lxml.etree.HTMLParser()


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    return _http.request(url)[1]


def _get_descr(url):
    return json.loads(_fetch(url).decode())['edesc']


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('item_href')
        key = href[href.rindex('/') + 1:]
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    if channel != 'ICTV':
        return []

    today = dateutil.tv_date_now(_source_tz, 5)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        url = d.strftime(_SCHED_URL)
        doc = lxml.etree.fromstring(_fetch(url), _parser)
        for row in doc[1][4][1][0][5][2][4][0][::2]:
            it = row.iterchildren()
            sched.set_time(next(it).text)
            a = next(it)[0]
            sched.set_title(a.text)
            sched.set_descr(descriptions.get(a))
        d += _daydelta
    return sched.pop()
