import datetime
import urllib.parse
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://ntn.ua'
_SCHED_URL = '/uk/tv/%Y/%m/%d'
_source_tz = pytz.timezone('Europe/Kiev')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.html.fromstring(content)
    return doc[1][0][7][4][-1][0][0][0][0][0][0]


def _get_descr(url):
    return '/n'.join(x.text or '' for x in _fetch(url)[2][2][-1])


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = href[href.rindex('/') + 1:]
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    if channel != 'НТН':
        return []

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        for event in _fetch(d.strftime(_SCHED_URL))[3][1]:
            it = event.iterchildren()
            sched.set_time(next(it).text)
            info = next(it)
            if len(info) == 0:
                sched.set_title(info.text.strip())
            else:
                a = info[0]
                sched.set_title(a.text)
                sched.set_descr(descriptions.get(a))
        d += _daydelta
    return sched.pop()
