import urllib.parse
import itertools
import pytz
import requests
import lxml.html
from tv_schedule import schedule, dateutil


def need_channel_code():
    return False

_URL = 'http://tvzvezda.ru'
_SCHED_URL = '/schedule/'
_source_tz = pytz.timezone('Europe/Moscow')


def _fetch(url):
    url = urllib.parse.urljoin(_URL, url)
    resp = requests.get(url)
    doc = lxml.html.fromstring(resp.content)
    table = next(doc[2].iterchildren('table'))
    toptable = table[-1][0][0]
    central = next(x[0] for x in toptable if x[0].get('class') == 'central')
    return central[0][0][0][0][0][1]


def _get_descr(url):
    try:
        cell = next(x[0] for x in _fetch(url)[0]
                    if x[0].get('class') == 'newstext')
    except StopIteration:
        pass
    else:
        for br in cell.iter('br'):
            br.tail = '\n' + br.tail if br.tail else '\n'
        return cell.text_content()


def _get_leaf(a):
    return a if len(a) == 0 else a[0]


class _Descriptions:
    def __init__(self):
        self._cash = {}

    def get(self, a):
        href = a.get('href')
        key = _get_leaf(a).text
        descr = self._cash.get(key)
        if descr is None:
            self._cash[key] = descr = _get_descr(href) or ''
        return descr


def get_schedule(channel, tz):
    if channel != 'Звезда':
        return []

    descriptions = _Descriptions()
    sched = schedule.Schedule(tz, _source_tz)

    table = _fetch(_SCHED_URL)[0]
    it = itertools.islice(table, 3, None, 2)
    row1 = next(it)
    days = (x[0] for x in row1[0][0][0][1:])
    row2 = next(it)
    tabs = (x[0] for x in row2[0])
    for day, tab in zip(days, tabs):
        d = dateutil.parse_date(day[0][0][0].text + day[1][0].text, '%a%d.%m')
        sched.set_date(d)
        for event in tab:
            it = event.iterchildren()
            sched.set_time(next(it).text)
            a = next(it)[0]
            sched.set_title(_get_leaf(a).text)
            sched.set_descr(descriptions.get(a))
    return sched.pop()
