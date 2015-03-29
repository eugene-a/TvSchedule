import datetime
import urllib.parse
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil

def need_channel_code():
    return False

_URL = 'http://www.1plus1.ua'
_SCHED_URL = '/teleprograma/%Y-%m-%d'

_source_tz = pytz.timezone('Europe/Kiev')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.html.fromstring(content)
    if doc[1].tag == 'script':
        return doc[3][7][3][1]


def _get_descr(url):
    left = _fetch(url)
    if left is not None:
        return '\n'.join(x.text_content() for x in left[1][0].iter('p'))


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = href[href[: -5].rindex('/') + 1: -5]
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    if channel != '1+1':
        return []
    descriptions = _Descriptions()

    sched = schedule.Schedule(tz, _source_tz)

    today = dateutil.tv_date_now(_source_tz)
    weekday_now = today.weekday()

    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        for li in _fetch(d.strftime(_SCHED_URL))[0][3]:
            short = li[0]
            sched.set_time(short[0].text)
            title = short[1]
            if len(title) == 0:
                sched.set_title(title.text)
            else:
                a = title[0]
                sched.set_title(a.text)
                descr = descriptions.get(a) or li[1][1][0].tail
                sched.set_descr(descr)

        d += _daydelta
    return sched.pop()
