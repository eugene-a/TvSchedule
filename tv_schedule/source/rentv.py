import datetime
import itertools
import urllib.parse
import pytz
import requests
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://ren.tv'
_SCHED_URL = '/tv-programma'

_source_tz = pytz.timezone('Europe/Moscow')
_daydelta = datetime.timedelta(1)


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url)
    doc = lxml.html.fromstring(resp.content)
    content = doc[2].get_element_by_id('content')
    return content[1][0][0]


def _get_descr(url):
    try:
        section = next(
           itertools.islice(_fetch(url).iterchildren('section'), 1, None)
        )
    except StopIteration:
        pass
    else:
        return '\n'.join(x.text_content() for x in section.iter('p'))


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        if href.startswith('node/') and len(href) > 5:
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

    for date_row in _fetch(_SCHED_URL)[3][0][0][1]:
        it = date_row.iterchildren()
        div = next(it)[0][0]
        date = div.text + ' ' + div.tail
        sched.set_date(dateutil.parse_date(date, '%a %d %B'))

        for info in (x[1] for x in next(it)):
            it = info.iterchildren()
            sched.set_time(next(it)[0][0].text)
            a = next(it)[0][1]
            sched.set_title(a.text)
            descr = descriptions.get(a)
            if descr:
                sched.set_descr(descr)
    return sched.pop()
