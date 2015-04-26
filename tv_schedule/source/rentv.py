import datetime
import itertools
import urllib.parse
import pytz
import httplib2
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://ren.tv'
_SCHED_URL = '/tv-programma'

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)

_http = httplib2.Http()


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    content = _http.request(url)[1]
    doc = lxml.html.fromstring(content)
    return doc[2][6][0][3][0][1][0][1][1][0]


def _get_descr(url):
    section = next(
        itertools.islice(_fetch(url).iterchildren('section'), 1, None)
    )
    return '\n'.join(x.text_content() for x in section.iter('p'))


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        if href.startswith('node/'):
            key = int(href[5:])
            descr = self._cash.get(key)
            if descr is None:
                self._cash[key] = descr = _get_descr(href)
            return descr


def get_schedule(channel, tz):
    if channel != 'РЕН ТВ':
        return []

    sched = schedule.Schedule(tz, _source_tz)
    descriptions = _Descriptions()

    for date_raw in _fetch(_SCHED_URL)[3][0][0][1]:
        div = date_raw[0][0][0]
        date = div.text + ' ' + div.tail
        sched.set_date(dateutil.parse_date(date, '%a %d %B'))

        for cell in date_raw[1]:
            info = cell[1]
            sched.set_time(info[0][0][0].text)
            a = info[1][0][1]
            sched.set_title(a.text)
            descr = descriptions.get(a)
            if descr:
                sched.set_descr(descr)
    return sched.pop()
