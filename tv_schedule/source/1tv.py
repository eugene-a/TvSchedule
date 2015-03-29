import datetime
import urllib.parse
import pytz
import httplib2
import lxml.etree
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://1tv.com.ua'
_SCHED_URL = '/uk/tv/%Y/%m/%d'
_source_tz = pytz.timezone('Europe/Kiev')
_daydelta = datetime.timedelta(1)
_http = httplib2.Http()
_parser = lxml.etree.HTMLParser()


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.etree.fromstring(content, _parser)
    return doc[1][2][0][1][0][0][2]


def _get_descr(url):
    return '\n'.join((x.text or '') for x in _fetch(url)[-1])


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, ts1):
        href = ts1[0][0].get('href')
        spl = href.split('/')
        if len(spl) > 4:
            descr = _get_descr(href)
        else:
            key = spl[-1]
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href)
        return descr


def get_schedule(channel, tz):
    if channel != 'Перший Національний / Ера':
        return []

    today = dateutil.tv_date_now(_source_tz)

    weekday_now = today.weekday()
    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()
    d = today
    for i in range(weekday_now, 7):
        sched.set_date(d)
        for event in _fetch(d.strftime(_SCHED_URL))[0][3]:
            it = event.iterchildren()
            sched.set_time(next(it).text)
            cell = next(it)
            it = cell.iterchildren()
            title = next(it)
            if len(title) == 0:
                sched.set_title(title.text)
            else:
                sched.set_title(title[0].text)
                sched.set_descr(descriptions.get(next(it)))
        d += _daydelta
    return sched.pop()
