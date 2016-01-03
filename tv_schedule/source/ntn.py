import datetime
import urllib.parse
import pytz
import requests
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://ntn.ua'
_SCHED_URL = '/uk/tv/%Y/%m/%d'
_source_tz = pytz.timezone('Europe/Kiev')
_daydelta = datetime.timedelta(1)


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url)
    doc = lxml.html.fromstring(resp.content)
    body = next(x for x in doc[1] if x.get('id') == 'body')
    return body[7][5][-1][0][0][0][0][0][0]


def _get_descr(url):
    b_block = _fetch(url)
    if len(b_block) < 3:
        return ''
    else:
        return '\n'.join(x.text or '' for x in b_block[2][2][-1])


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
                a = info[-2]
                sched.set_title(a.text)
                sched.set_descr(descriptions.get(a))
        d += _daydelta
    return sched.pop()
